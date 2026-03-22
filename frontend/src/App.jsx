import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Layout, Menu, Badge } from 'antd'
import {
  DashboardOutlined,
  TeamOutlined,
  ProjectOutlined,
  MessageOutlined,
  RobotOutlined
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Projects from './pages/Projects'
import Tasks from './pages/Tasks'

const { Header, Sider, Content } = Layout

function App() {
  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">看板总览</Link>
    },
    {
      key: '/agents',
      icon: <TeamOutlined />,
      label: <Link to="/agents">Agent 管理</Link>
    },
    {
      key: '/projects',
      icon: <ProjectOutlined />,
      label: <Link to="/projects">项目管理</Link>
    },
    {
      key: '/tasks',
      icon: <RobotOutlined />,
      label: <Link to="/tasks">任务看板</Link>
    }
  ]

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header className="header">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <RobotOutlined style={{ fontSize: 24, marginRight: 12 }} />
            <h1>Buddy Dashboard</h1>
          </div>
          <div className="header-right">
            <Badge count={3}>
              <MessageOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
            </Badge>
          </div>
        </Header>
        
        <Layout>
          <Sider width={200} style={{ background: '#fff' }}>
            <Menu
              mode="inline"
              defaultSelectedKeys={['/']}
              style={{ height: '100%', borderRight: 0 }}
              items={menuItems}
            />
          </Sider>
          
          <Layout style={{ padding: '0' }}>
            <Content style={{ background: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/agents" element={<Agents />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/tasks" element={<Tasks />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  )
}

export default App
