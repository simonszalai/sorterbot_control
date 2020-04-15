import React from 'react'
import { ThemeProvider } from 'emotion-theming'
import styled from '@emotion/styled'
import 'App.css'

import theme from './theme'
import Header from 'components/Header'
import ArmsList from 'components/ArmsList'
import SessionsList from 'components/SessionsList'


function App() {
  return (
    <ThemeProvider theme={theme}>
      <Body>
        <Header />
        <Main>
          <ArmsList />
          <SessionsList />
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
  padding-right: 15px;
  position: relative;
  width: 70vw;
  min-height: 50vh;
  max-height: 60vh;
  z-index: 10;
  ${props => props.theme.shadow('box')}
`