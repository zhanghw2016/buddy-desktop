import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Tag, Progress, List, Avatar, Typography } from 'antd'
import {
  TeamOutlined,
  ProjectOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined
} from '@ant-design/icons'
import { projectAPI, taskAPI, agentAPI } from '../services/api'

const { Title, Text } = Typography

function Dashboard() {
  const [agents, setAgents] = useState([])
  const [projects, setProjects] = useState([])
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [agentsRes, projectsRes, tasksRes] = await Promise.all([
        agentAPI.getAll(),
        projectAPI.getAll(),
        taskAPI.getAll()
      ])
      
      setAgents(agentsRes.data || [])
      setProjects(projectsRes.data || [])
      setTasks(tasksRes.data || [])
    } catch (error) {
      console.error('加载数据失败:', error)
      // 使用模拟数据
      setAgents([
        { id: '1', name: '林经理', role: 'pm', status: 'idle', capabilities: ['需求分析', '任务分配'] },
        { id: '2', name: '秦设计', role: 'ui', status: 'working', capabilities: ['UI设计', '原型制作'] },
        { id: '3', name: '张开发', role: 'backend', status: 'working', capabilities: ['后端开发', 'API设计'] },
        { id: '4', name: '王测试', role: 'qa', status: 'idle', capabilities: ['测试用例', 'Bug分析'] }
      ])
      setProjects([
        { id: '1', name: 'VDI 桌面管理系统优化', status: 'in_progress', progress: 65 },
        { id: '2', name: '看板系统开发', status: 'in_progress', progress: 30 }
      ])
      setTasks([
        { id: '1', title: '优化桌面组创建性能', status: 'in_progress', priority: 'high', assignee: '张开发' },
        { id: '2', title: '修复用户登录偶发失败问题', status: 'completed', priority: 'high', assignee: '张开发' },
        { id: '3', title: '编写 API 性能测试用例', status: 'pending', priority: 'medium', assignee: '王测试' },
        { id: '4', title: '设计看板 UI 原型', status: 'in_progress', priority: 'high', assignee: '秦设计' }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'idle': '#8c8c8c',
      'working': '#1890ff',
      'offline': '#ff4d4f'
    }
    return colors[status] || '#8c8c8c'
  }

  const getRoleName = (role) => {
    const names = {
      'pm': '项目经理',
      'ui': 'UI设计师',
      'backend': '后端开发',
      'qa': '测试工程师'
    }
    return names[role] || role
  }

  const getTaskStatusColor = (status) => {
    const colors = {
      'pending': 'default',
      'in_progress': 'processing',
      'completed': 'success',
      'blocked': 'error'
    }
    return colors[status] || 'default'
  }

  const taskStats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    inProgress: tasks.filter(t => t.status === 'in_progress').length,
    pending: tasks.filter(t => t.status === 'pending').length
  }

  return (
    <div className="main-content">
      <Title level={2}>看板总览</Title>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Agent 总数"
              value={agents.length}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={projects.length}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="任务总数"
              value={taskStats.total}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成任务"
              value={taskStats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Agent 状态 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="Agent 状态" extra={<a href="/agents">查看全部</a>}>
            <List
              dataSource={agents}
              renderItem={agent => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        style={{ backgroundColor: getStatusColor(agent.status) }}
                        icon={<UserOutlined />}
                      />
                    }
                    title={
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{agent.name}</span>
                        <Tag color={getStatusColor(agent.status)}>
                          {agent.status === 'working' ? '工作中' : agent.status === 'idle' ? '空闲' : '离线'}
                        </Tag>
                      </div>
                    }
                    description={getRoleName(agent.role)}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card title="项目进度">
            {projects.map(project => (
              <div key={project.id} style={{ marginBottom: 20 }}>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>{project.name}</Text>
                  <Tag color="blue" style={{ marginLeft: 8 }}>
                    {project.status === 'in_progress' ? '进行中' : '已完成'}
                  </Tag>
                </div>
                <Progress percent={project.progress || 0} status="active" />
              </div>
            ))}
          </Card>
        </Col>
      </Row>

      {/* 最近任务 */}
      <Card title="最近任务" style={{ marginTop: 16 }} extra={<a href="/tasks">查看全部</a>}>
        <List
          dataSource={tasks.slice(0, 5)}
          renderItem={task => (
            <List.Item>
              <List.Item.Meta
                title={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span>{task.title}</span>
                    <Tag color={getTaskStatusColor(task.status)}>
                      {task.status === 'in_progress' ? '进行中' : 
                       task.status === 'completed' ? '已完成' : 
                       task.status === 'pending' ? '待处理' : '阻塞'}
                    </Tag>
                  </div>
                }
                description={
                  <div style={{ display: 'flex', gap: 16 }}>
                    <span>负责人: {task.assignee}</span>
                    <Tag color={task.priority === 'high' ? 'red' : task.priority === 'medium' ? 'orange' : 'default'}>
                      {task.priority === 'high' ? '高优先级' : 
                       task.priority === 'medium' ? '中优先级' : '低优先级'}
                    </Tag>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  )
}

export default Dashboard
