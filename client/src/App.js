import React, { useEffect, useState } from 'react'
import { ThemeProvider } from 'emotion-theming'
import styled from '@emotion/styled'
import 'App.css'

import WS from 'webSocketService'
import theme from './theme'
import Header from 'components/Header'
import ArmsList from 'components/ArmsList'
import SessionsList from 'components/SessionsList'
import Logs from 'components/Logs'


function App() {
  const [logs, setLogs] = useState([])
  const [selectedArm, setSelectedArm] = useState(null)

  useEffect(() => {
    WS.connect()
    WS.addCallbacks([{
      command: 'fetch_logs', fn: (data) => {
      console.log("App -> data", data)
        setLogs(data.logs)
        }
    }])
    WS.sendMessage({ command: 'set_open_logs', open_logs: 'none'})
  }, [])

  return (
    <ThemeProvider theme={theme}>
      <Body>
        <Header />
        <Main>
          <ArmsList
            selectedArm={selectedArm}
            setSelectedArm={setSelectedArm}
          />
          <SessionsList selectedArm={selectedArm} />
          <Logs logs={logs} />
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
  min-height: 50vh;
  max-height: 60vh;
  z-index: 10;
  ${props => props.theme.shadow('box')}
`