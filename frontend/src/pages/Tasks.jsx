import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Tag, Typography, Button, Modal, Form, Input, Select, InputNumber, DatePicker, message } from 'antd'
import { PlusOutlined, DragOutlined } from '@ant-design/icons'
import { taskAPI, agentAPI } from '../services/api'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TextArea } = Input

function Tasks() {
  const [tasks, setTasks] = useState([])
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [tasksRes, agentsRes] = await Promise.all([
        taskAPI.getAll(),
        agentAPI.getAll()
      ])
      setTasks(tasksRes.data || [])
      setAgents(agentsRes.data || [])
    } catch (error) {
      console.error('加载数据失败:', error)
      // 使用模拟数据
      setTasks([
        {
          id: '1',
          title: '优化桌面组创建性能',
          description: '优化桌面组创建流程，减少响应时间',
          type: 'development',
          priority: 'high',
          status: 'in_progress',
          assignee: '张开发',
          estimated_hours: 16,
          actual_hours: 8,
          due_date: dayjs().add(7, 'days')
        },
        {
          id: '2',
          title: '修复用户登录偶发失败问题',
          description: '排查并修复用户登录时偶发的认证失败问题',
          type: 'bug',
          priority: 'high',
          status: 'completed',
          assignee: '张开发',
          estimated_hours: 4,
          actual_hours: 3,
          due_date: dayjs().subtract(2, 'days')
        },
        {
          id: '3',
          title: '编写 API 性能测试用例',
          description: '为核心 API 接口编写性能测试用例',
          type: 'test',
          priority: 'medium',
          status: 'pending',
          assignee: '王测试',
          estimated_hours: 8,
          due_date: dayjs().add(5, 'days')
        },
        {
          id: '4',
          title: '设计看板 UI 原型',
          description: '设计项目管理看板的 UI 原型和交互流程',
          type: 'design',
          priority: 'high',
          status: 'in_progress',
          assignee: '秦设计',
          estimated_hours: 12,
          due_date: dayjs().add(10, 'days')
        }
      ])
      
      setAgents([
        { id: '1', name: '林经理', role: 'pm' },
        { id: '2', name: '秦设计', role: 'ui' },
        { id: '3', name: '张开发', role: 'backend' },
        { id: '4', name: '王测试', role: 'qa' }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getStatusInfo = (status) => {
    const info = {
      'pending': { text: '待处理', color: 'default' },
      'in_progress': { text: '进行中', color: 'processing' },
      'completed': { text: '已完成', color: 'success' },
      'blocked': { text: '阻塞', color: 'error' },
      'cancelled': { text: '已取消', color: 'default' }
    }
    return info[status] || info['pending']
  }

  const getPriorityInfo = (priority) => {
    const info = {
      'high': { text: '高', color: 'red' },
      'medium': { text: '中', color: 'orange' },
      'low': { text: '低', color: 'default' }
    }
    return info[priority] || info['medium']
  }

  const getTypeInfo = (type) => {
    const info = {
      'requirement': { text: '需求', color: 'purple' },
      'design': { text: '设计', color: 'magenta' },
      'development': { text: '开发', color: 'blue' },
      'test': { text: '测试', color: 'green' },
      'bug': { text: 'Bug', color: 'red' },
      'documentation': { text: '文档', color: 'cyan' }
    }
    return info[type] || info['development']
  }

  // 按状态分组
  const tasksByStatus = {
    pending: tasks.filter(t => t.status === 'pending'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    completed: tasks.filter(t => t.status === 'completed'),
    blocked: tasks.filter(t => t.status === 'blocked')
  }

  const handleCreateTask = async (values) => {
    try {
      await taskAPI.create(values)
      message.success('任务创建成功')
      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error) {
      message.error('任务创建失败')
      console.error('创建任务失败:', error)
    }
  }

  const renderTaskCard = (task) => {
    const statusInfo = getStatusInfo(task.status)
    const priorityInfo = getPriorityInfo(task.priority)
    const typeInfo = getTypeInfo(task.type)
    
    return (
      <Card 
        key={task.id}
        className="task-card"
        size="small"
        hoverable
        style={{ marginBottom: 12 }}
      >
        <div style={{ marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
            <Tag color={typeInfo.color}>{typeInfo.text}</Tag>
            <Tag color={priorityInfo.color}>{priorityInfo.text}优先级</Tag>
          </div>
          <Text strong style={{ fontSize: 14 }}>{task.title}</Text>
        </div>
        
        <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
          {task.description}
        </Text>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            负责人: <Text strong>{task.assignee}</Text>
          </Text>
          {task.due_date && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              截止: {dayjs(task.due_date).format('MM-DD')}
            </Text>
          )}
        </div>
      </Card>
    )
  }

  return (
    <div className="main-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>任务看板</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          新建任务
        </Button>
      </div>
      
      {/* 看板列 */}
      <Row gutter={16}>
        <Col span={6}>
          <Card title="待处理" style={{ background: '#fafafa' }}>
            <div className="kanban-column">
              {tasksByStatus.pending.map(renderTaskCard)}
            </div>
          </Card>
        </Col>
        
        <Col span={6}>
          <Card title="进行中" style={{ background: '#fafafa' }}>
            <div className="kanban-column">
              {tasksByStatus.in_progress.map(renderTaskCard)}
            </div>
          </Card>
        </Col>
        
        <Col span={6}>
          <Card title="已完成" style={{ background: '#fafafa' }}>
            <div className="kanban-column">
              {tasksByStatus.completed.map(renderTaskCard)}
            </div>
          </Card>
        </Col>
        
        <Col span={6}>
          <Card title="阻塞" style={{ background: '#fafafa' }}>
            <div className="kanban-column">
              {tasksByStatus.blocked.map(renderTaskCard)}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 新建任务模态框 */}
      <Modal
        title="新建任务"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateTask}
        >
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="title"
                label="任务标题"
                rules={[{ required: true, message: '请输入任务标题' }]}
              >
                <Input placeholder="请输入任务标题" />
              </Form.Item>
            </Col>
            
            <Col span={24}>
              <Form.Item
                name="description"
                label="任务描述"
              >
                <TextArea rows={4} placeholder="请输入任务描述" />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="type"
                label="任务类型"
                rules={[{ required: true, message: '请选择任务类型' }]}
              >
                <Select placeholder="请选择任务类型">
                  <Select.Option value="requirement">需求</Select.Option>
                  <Select.Option value="design">设计</Select.Option>
                  <Select.Option value="development">开发</Select.Option>
                  <Select.Option value="test">测试</Select.Option>
                  <Select.Option value="bug">Bug</Select.Option>
                  <Select.Option value="documentation">文档</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="priority"
                label="优先级"
                rules={[{ required: true, message: '请选择优先级' }]}
              >
                <Select placeholder="请选择优先级">
                  <Select.Option value="high">高</Select.Option>
                  <Select.Option value="medium">中</Select.Option>
                  <Select.Option value="low">低</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="assignee"
                label="负责人"
                rules={[{ required: true, message: '请选择负责人' }]}
              >
                <Select placeholder="请选择负责人">
                  {agents.map(agent => (
                    <Select.Option key={agent.id} value={agent.name}>
                      {agent.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="estimated_hours"
                label="预估工时（小时）"
              >
                <InputNumber min={0} style={{ width: '100%' }} placeholder="请输入预估工时" />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="due_date"
                label="截止日期"
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default Tasks
