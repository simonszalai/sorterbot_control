import React, { useEffect, useState } from 'react'
import { ThemeProvider } from 'emotion-theming'
import styled from '@emotion/styled'
import 'App.css'

import WS from 'webSocketService'
import theme from './theme'
import Header from 'components/Header'
import ArmsList from 'components/ArmsList'
import SessionsList from 'components/SessionsList'
import Content from 'components/Content'


function App() {
  const [logs, setLogs] = useState([])
  const [selectedArm, setSelectedArm] = useState(null)
  const [expandedSessionId, setExpandedSessionId] = useState(null)
  const [selectedLog, setSelectedLog] = useState([])
  const [stitchUrl, setStitchUrl] = useState(null)

  useEffect(() => {
    WS.connect()
    WS.addCallbacks([{ command: 'stitch', fn: (data) => setStitchUrl(data.stitch_url) }])
    WS.addCallbacks([{ command: 'logs', fn: (data) => setLogs(data.logs) }])
    WS.sendMessage({ command: 'set_open_logs', open_logs: 'none'})
  }, [])

  console.log("App -> selectedArm", selectedArm)
  return (
    <ThemeProvider theme={theme}>
      <Body>
        <Header />
        <Main>
          <ArmsList
            selectedArm={selectedArm}
            setSelectedArm={setSelectedArm}
            setLogs={setLogs}
            setExpandedSessionId={setExpandedSessionId}
            setSelectedLog={setSelectedLog}
          />
          <SessionsList
            selectedArm={selectedArm}
            expandedSessionId={expandedSessionId}
            setExpandedSessionId={setExpandedSessionId}
            selectedLog={selectedLog}
            setSelectedLog={setSelectedLog}
            setLogs={setLogs}
            setStitchUrl={setStitchUrl}
          />
          <Content
            logs={logs}
            stitchUrl={stitchUrl}
          />
        </Main>
      </Body>
    </ThemeProvider>
  )
}

export default App



const Body = styled.div`
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding-bottom: 3vw;
`

  const Main = styled.div`
  background-color: #fff;
  border-radius: 4px;
  display: flex;
  flex: 1;
  margin-top: 75px;
  overflow: hidden;
  padding-left: 15px;
  position: relative;
  width: 70vw;
  min-height: 80vh;
  max-height: 80vh;
  z-index: 10;
  ${props => props.theme.shadow('box')}
  transition: all 0.3s ease-in-out;
`