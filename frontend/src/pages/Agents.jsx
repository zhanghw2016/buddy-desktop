import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Avatar, Tag, Descriptions, List, Typography, Badge } from 'antd'
import {
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  MinusCircleOutlined
} from '@ant-design/icons'
import { agentAPI } from '../services/api'

const { Title, Text } = Typography

function Agents() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const res = await agentAPI.getAll()
      setAgents(res.data || [])
    } catch (error) {
      console.error('加载 Agent 失败:', error)
      // 使用模拟数据
      setAgents([
        {
          id: '1',
          name: '林经理',
          role: 'pm',
          status: 'idle',
          capabilities: ['需求分析', '任务分配', '进度跟踪', '风险管理'],
          current_task: null,
          completed_tasks: 15,
          config: { ai_model: 'local', max_tasks: 10 }
        },
        {
          id: '2',
          name: '秦设计',
          role: 'ui',
          status: 'working',
          capabilities: ['UI设计', '原型制作', '交互设计', '视觉设计'],
          current_task: '设计看板 UI 原型',
          completed_tasks: 12,
          config: { ai_model: 'local', max_tasks: 8 }
        },
        {
          id: '3',
          name: '张开发',
          role: 'backend',
          status: 'working',
          capabilities: ['后端开发', 'API设计', '数据库设计', '性能优化'],
          current_task: '优化桌面组创建性能',
          completed_tasks: 20,
          config: { ai_model: 'local', max_tasks: 12 }
        },
        {
          id: '4',
          name: '王测试',
          role: 'qa',
          status: 'idle',
          capabilities: ['测试用例', 'Bug分析', '性能测试', '自动化测试'],
          current_task: null,
          completed_tasks: 18,
          config: { ai_model: 'local', max_tasks: 10 }
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getStatusInfo = (status) => {
    const info = {
      'idle': { text: '空闲', color: '#8c8c8c', icon: <MinusCircleOutlined /> },
      'working': { text: '工作中', color: '#1890ff', icon: <ClockCircleOutlined /> },
      'offline': { text: '离线', color: '#ff4d4f', icon: <MinusCircleOutlined /> }
    }
    return info[status] || info['idle']
  }

  const getRoleInfo = (role) => {
    const info = {
      'pm': { name: '项目经理', color: '#722ed1' },
      'ui': { name: 'UI设计师', color: '#eb2f96' },
      'backend': { name: '后端开发', color: '#1890ff' },
      'qa': { name: '测试工程师', color: '#52c41a' }
    }
    return info[role] || { name: role, color: '#8c8c8c' }
  }

  return (
    <div className="main-content">
      <Title level={2}>Agent 管理</Title>
      
      <Row gutter={[16, 16]}>
        {agents.map(agent => {
          const statusInfo = getStatusInfo(agent.status)
          const roleInfo = getRoleInfo(agent.role)
          
          return (
            <Col span={12} key={agent.id}>
              <Card className="agent-card">
                <div style={{ display: 'flex', alignItems: 'start', marginBottom: 16 }}>
                  <Badge 
                    dot 
                    color={statusInfo.color}
                    offset={[-5, 5]}
                  >
                    <Avatar 
                      size={64} 
                      style={{ backgroundColor: roleInfo.color }}
                      icon={<UserOutlined />}
                    />
                  </Badge>
                  
                  <div style={{ marginLeft: 16, flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <Title level={4} style={{ margin: 0 }}>{agent.name}</Title>
                      <Tag color={roleInfo.color}>{roleInfo.name}</Tag>
                    </div>
                    
                    <Tag color={statusInfo.color} icon={statusInfo.icon}>
                      {statusInfo.text}
                    </Tag>
                    
                    {agent.current_task && (
                      <div style={{ marginTop: 8 }}>
                        <Text type="secondary">当前任务: </Text>
                        <Text strong>{agent.current_task}</Text>
                      </div>
                    )}
                  </div>
                </div>

                <Descriptions column={2} size="small">
                  <Descriptions.Item label="已完成任务">
                    <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
                      {agent.completed_tasks || 0}
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="最大任务数">
                    {agent.config?.max_tasks || 10}
                  </Descriptions.Item>
                </Descriptions>

                <div style={{ marginTop: 16 }}>
                  <Text type="secondary" strong>能力标签:</Text>
                  <div style={{ marginTop: 8 }}>
                    {agent.capabilities?.map((cap, index) => (
                      <Tag key={index} style={{ marginBottom: 4 }}>{cap}</Tag>
                    ))}
                  </div>
                </div>
              </Card>
            </Col>
          )
        })}
      </Row>
    </div>
  )
}

export default Agents
