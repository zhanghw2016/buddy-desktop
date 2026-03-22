import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Progress, Tag, Typography, List, Button, Modal, Form, Input, DatePicker, Select } from 'antd'
import { PlusOutlined, ProjectOutlined } from '@ant-design/icons'
import { projectAPI } from '../services/api'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { RangePicker } = DatePicker

function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const res = await projectAPI.getAll()
      setProjects(res.data || [])
    } catch (error) {
      console.error('加载项目失败:', error)
      // 使用模拟数据
      setProjects([
        {
          id: '1',
          name: 'VDI 桌面管理系统优化',
          description: '对现有 VDI 桌面管理系统进行性能优化和功能增强',
          status: 'in_progress',
          owner: '林经理',
          start_date: dayjs().subtract(30, 'days'),
          end_date: dayjs().add(60, 'days'),
          progress: 65,
          task_count: 3
        },
        {
          id: '2',
          name: '看板系统开发',
          description: '开发基于 AI Agent 的项目管理看板系统',
          status: 'in_progress',
          owner: '林经理',
          start_date: dayjs().subtract(15, 'days'),
          end_date: dayjs().add(45, 'days'),
          progress: 30,
          task_count: 1
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getStatusInfo = (status) => {
    const info = {
      'planning': { text: '规划中', color: 'default' },
      'in_progress': { text: '进行中', color: 'processing' },
      'on_hold': { text: '暂停', color: 'warning' },
      'completed': { text: '已完成', color: 'success' },
      'cancelled': { text: '已取消', color: 'error' }
    }
    return info[status] || info['planning']
  }

  const handleCreateProject = async (values) => {
    try {
      await projectAPI.create(values)
      setModalVisible(false)
      form.resetFields()
      loadProjects()
    } catch (error) {
      console.error('创建项目失败:', error)
    }
  }

  return (
    <div className="main-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>项目管理</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          新建项目
        </Button>
      </div>
      
      <Row gutter={[16, 16]}>
        {projects.map(project => {
          const statusInfo = getStatusInfo(project.status)
          const daysLeft = project.end_date ? dayjs(project.end_date).diff(dayjs(), 'days') : 0
          
          return (
            <Col span={12} key={project.id}>
              <Card 
                hoverable 
                style={{ borderRadius: 8 }}
                title={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <ProjectOutlined style={{ color: '#1890ff' }} />
                    <span>{project.name}</span>
                    <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
                  </div>
                }
              >
                <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
                  {project.description}
                </Text>

                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text strong>项目进度</Text>
                    <Text>{project.progress || 0}%</Text>
                  </div>
                  <Progress 
                    percent={project.progress || 0} 
                    status={project.progress === 100 ? 'success' : 'active'}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text type="secondary">负责人: </Text>
                    <Text strong>{project.owner}</Text>
                  </div>
                  <div>
                    <Text type="secondary">任务数: </Text>
                    <Text strong>{project.task_count || 0}</Text>
                  </div>
                </div>

                {daysLeft > 0 && (
                  <div style={{ marginTop: 12, textAlign: 'right' }}>
                    <Tag color="blue">剩余 {daysLeft} 天</Tag>
                  </div>
                )}
              </Card>
            </Col>
          )
        })}
      </Row>

      {/* 新建项目模态框 */}
      <Modal
        title="新建项目"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateProject}
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="项目描述"
          >
            <Input.TextArea rows={4} placeholder="请输入项目描述" />
          </Form.Item>

          <Form.Item
            name="dateRange"
            label="项目周期"
          >
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Projects
