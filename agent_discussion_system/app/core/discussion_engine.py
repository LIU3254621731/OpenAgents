#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讨论引擎类

该模块是多智能体讨论系统的核心引擎，负责驱动整个讨论过程，包括：
- 管理讨论流程
- 协调多个智能体的发言
- 处理控制指令
- 实现多种终止条件
- 生成讨论总结

采用QThread实现，确保讨论过程在后台线程中执行，不阻塞UI。
"""

import time
from typing import List, Dict, Any
from PySide6.QtCore import QThread, Signal
from app.core.workflow_manager import WorkflowManager
from app.core.agent import Agent, AgentPermission
from app.models.model_adapter import ModelAdapter
from app.utils.logger import get_logger

logger = get_logger()


class DiscussionEngine(QThread):
    """讨论引擎类
    
    负责驱动整个多智能体讨论过程，在后台线程中执行，通过信号与UI交互。
    
    信号：
        - message_generated: 当智能体生成消息时发出
        - discussion_started: 当讨论开始时发出
        - discussion_ended: 当讨论结束时发出
        - round_changed: 当讨论轮次改变时发出
        - status_updated: 当讨论状态更新时发出
    """
    
    # 信号定义
    message_generated = Signal(dict)  # 消息生成信号，包含agent_id、name、content等
    discussion_started = Signal()     # 讨论开始信号
    discussion_ended = Signal(dict)   # 讨论结束信号，包含讨论结果
    round_changed = Signal(int)       # 轮次改变信号，包含当前轮次
    status_updated = Signal(str)      # 状态更新信号，包含状态描述
    
    def __init__(self, workflow_manager: WorkflowManager, model_adapter: ModelAdapter):
        """初始化讨论引擎
        
        Args:
            workflow_manager (WorkflowManager): 流程管理器实例
            model_adapter (ModelAdapter): 模型适配器实例
        """
        super().__init__()
        
        self.workflow_manager = workflow_manager
        self.model_adapter = model_adapter
        
        # 讨论状态
        self.is_running = False
        self.is_paused = False
        self.is_terminated = False
        
        # 讨论参数
        self.discussion_topic = ""
        self.discussion_history = []  # 完整讨论历史
        self.start_time = 0           # 讨论开始时间
        self.current_round_start_time = 0  # 当前轮次开始时间
        
        # 终止条件
        self.max_rounds = 10          # 最大轮次
        self.max_time_per_round = 60  # 每轮最大时间（秒）
        self.max_total_time = 300     # 总最大时间（秒）
    
    def set_topic(self, topic: str):
        """设置讨论主题
        
        Args:
            topic (str): 讨论主题
        """
        self.discussion_topic = topic
        logger.info(f"讨论主题已设置: {topic}")
    
    def set_termination_conditions(self, max_rounds: int, max_time_per_round: int, max_total_time: int):
        """设置终止条件
        
        Args:
            max_rounds (int): 最大轮次
            max_time_per_round (int): 每轮最大时间（秒）
            max_total_time (int): 总最大时间（秒）
        """
        self.max_rounds = max_rounds
        self.max_time_per_round = max_time_per_round
        self.max_total_time = max_total_time
        logger.info(f"终止条件已设置: 最大轮次={max_rounds}, 每轮最大时间={max_time_per_round}秒, 总最大时间={max_total_time}秒")
    
    def run(self):
        """线程主函数，启动讨论过程"""
        logger.info("讨论引擎启动")
        self.is_running = True
        self.is_paused = False
        self.is_terminated = False
        
        # 重置讨论状态
        self.discussion_history.clear()
        self.workflow_manager.reset()
        
        # 发出讨论开始信号
        self.discussion_started.emit()
        self.status_updated.emit("讨论开始")
        
        # 记录开始时间
        self.start_time = time.time()
        self.current_round_start_time = self.start_time
        
        try:
            # 主讨论循环
            while self.is_running:
                # 检查暂停状态
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                    
                if not self.is_running:
                    break
                
                # 检查终止条件
                if self._check_termination_conditions():
                    break
                
                # 获取下一个发言的智能体
                agent = self.workflow_manager.get_next_agent()
                if not agent:
                    logger.warning("没有可用的智能体，讨论结束")
                    break
                
                # 发出轮次改变信号
                current_round = self.workflow_manager.get_current_round()
                self.round_changed.emit(current_round)
                
                # 生成智能体的提示词
                prompt = agent.generate_prompt(self.discussion_topic, self.discussion_history[-5:] if len(self.discussion_history) > 5 else self.discussion_history)
                
                # 调用模型生成响应
                self.status_updated.emit(f"{agent.name}正在思考...")
                response = self.model_adapter.generate(prompt, agent.model_id)
                
                if not response:
                    logger.error(f"智能体 {agent.name} 生成响应失败")
                    continue
                
                # 处理智能体的响应
                processed_response = agent.process_response(response)
                
                # 记录讨论历史
                message = {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "role": "agent",
                    "content": processed_response["content"],
                    "timestamp": time.time(),
                    "round": current_round
                }
                
                self.discussion_history.append(message)
                agent.add_to_memory(message)
                
                # 发出消息生成信号
                self.message_generated.emit(message)
                
                # 处理控制指令
                if processed_response["control"]:
                    control_result = self.workflow_manager.process_control_command(agent, processed_response["control"])
                    if control_result["success"]:
                        self.status_updated.emit(control_result["message"])
                        
                        # 检查是否需要终止讨论
                        if control_result.get("terminate"):
                            logger.info("收到终止讨论指令，讨论结束")
                            break
                
                # 更新当前轮次开始时间
                if self.workflow_manager.current_agent_index == 0:
                    self.current_round_start_time = time.time()
            
        except Exception as e:
            logger.error(f"讨论引擎运行错误: {str(e)}")
            self.status_updated.emit(f"讨论发生错误: {str(e)}")
        finally:
            # 讨论结束处理
            self.is_running = False
            self._finish_discussion()
    
    def _check_termination_conditions(self) -> bool:
        """检查讨论是否满足终止条件
        
        Returns:
            bool: 满足终止条件返回True，否则返回False
        """
        current_time = time.time()
        current_round = self.workflow_manager.get_current_round()
        
        # 检查最大轮次
        if current_round >= self.max_rounds:
            logger.info(f"讨论达到最大轮次 {self.max_rounds}，讨论结束")
            self.status_updated.emit(f"讨论达到最大轮次 {self.max_rounds}")
            return True
        
        # 检查总最大时间
        total_time = current_time - self.start_time
        if total_time >= self.max_total_time:
            logger.info(f"讨论达到总最大时间 {self.max_total_time} 秒，讨论结束")
            self.status_updated.emit(f"讨论达到总最大时间 {self.max_total_time} 秒")
            return True
        
        # 检查每轮最大时间
        round_time = current_time - self.current_round_start_time
        if round_time >= self.max_time_per_round:
            logger.info(f"当前轮次达到最大时间 {self.max_time_per_round} 秒，讨论结束")
            self.status_updated.emit(f"当前轮次达到最大时间 {self.max_time_per_round} 秒")
            return True
        
        return False
    
    def _finish_discussion(self):
        """完成讨论，生成总结并发出结束信号"""
        logger.info("讨论引擎停止")
        
        # 生成讨论总结
        summary = self._generate_summary()
        
        # 发出讨论结束信号
        discussion_result = {
            "topic": self.discussion_topic,
            "history": self.discussion_history,
            "summary": summary,
            "rounds": self.workflow_manager.get_current_round(),
            "duration": time.time() - self.start_time,
            "terminated": self.is_terminated
        }
        
        self.discussion_ended.emit(discussion_result)
        self.status_updated.emit("讨论结束")
    
    def _generate_summary(self) -> str:
        """生成讨论总结
        
        Returns:
            str: 讨论总结
        """
        # 简单实现，未来可以使用AI生成更详细的总结
        summary = f"讨论主题：{self.discussion_topic}\n"
        summary += f"讨论轮次：{self.workflow_manager.get_current_round()}\n"
        summary += f"参与智能体：{', '.join([agent.name for agent in self.workflow_manager.get_agents().values()])}\n"
        summary += f"讨论结果：\n"
        
        # 添加每个智能体的最后一次发言
        last_messages = {}
        for message in self.discussion_history:
            last_messages[message["agent_id"]] = message
        
        for agent_id, message in last_messages.items():
            summary += f"\n{message['name']}: {message['content'][:100]}..."
        
        return summary
    
    def pause(self):
        """暂停讨论"""
        logger.info("讨论引擎暂停")
        self.is_paused = True
        self.status_updated.emit("讨论暂停")
    
    def resume(self):
        """恢复讨论"""
        logger.info("讨论引擎恢复")
        self.is_paused = False
        self.current_round_start_time = time.time()  # 重置轮次开始时间
        self.status_updated.emit("讨论恢复")
    
    def terminate(self):
        """终止讨论"""
        logger.info("讨论引擎终止")
        self.is_running = False
        self.is_paused = False
        self.is_terminated = True
        self.status_updated.emit("讨论终止")
    
    def get_discussion_history(self) -> List[Dict[str, Any]]:
        """获取讨论历史
        
        Returns:
            List[Dict[str, Any]]: 讨论历史列表
        """
        return self.discussion_history.copy()
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前讨论状态
        
        Returns:
            Dict[str, Any]: 当前讨论状态
        """
        current_time = time.time()
        total_time = current_time - self.start_time if self.start_time > 0 else 0
        round_time = current_time - self.current_round_start_time if self.current_round_start_time > 0 else 0
        
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "is_terminated": self.is_terminated,
            "current_round": self.workflow_manager.get_current_round(),
            "total_time": total_time,
            "round_time": round_time,
            "discussion_topic": self.discussion_topic,
            "participants": len(self.workflow_manager.get_agents())
        }
