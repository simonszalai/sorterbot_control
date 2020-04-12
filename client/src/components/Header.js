import React, { useState } from 'react'
import styled from '@emotion/styled'


const onRunningChange = (running, setRunning, setFaded) => {
  setFaded(true)
  setTimeout(() => {
    setRunning(!running)
    setFaded(false)
  }, 500)
}

const HeaderComponent = () => {
  const [running, setRunning] = useState(false)
  const [faded, setFaded] = useState(false)
  return (
    <Wrapper>
      <Header>
        <Logo src={require('assets/logo.png')} />
        <Right>
          <Text faded={faded}>
            <Span faded={faded}>{running ? 'SorterBot Cloud is running at: ' : 'Start sorterBot Cloud'}</Span>
            {running ? 'http://56.3.63.98:6000' : ''}
          </Text>
          <Btn
            faded={faded}
            onClick={() => onRunningChange(running, setRunning, setFaded)}
            src={require(`assets/${running ? 'stop' : 'start'}_white.svg`)}
          />
        </Right>
      </Header>
    </Wrapper>
  )
}

export default HeaderComponent



const Header = styled.div`
  display: flex;
  justify-content: space-between;
  padding-left: 10px;
  padding-right: 10px;
  width: 70vw;
`

const Wrapper = styled.div`
  background-color: ${props => props.theme.colors.dark};
  bottom: auto;
  box-shadow: none;
  display: flex;
  height: 140px;
  justify-content: center;
  left: 0%;
  position: absolute;
  right: 0%;
  top: 0%;
  width: 100%;
  z-index: 1;
`

const Logo = styled.img`
  height: 50px;
  margin-top: 10px;
`

const Right = styled.div`
  align-items: center;
  display: flex;
  flex-direction: row;
  height: 75px;
  justify-content: flex-start;
`

const Text = styled.div`
  color: #fff;
  font-family: Tahoma, Verdana, Segoe, sans-serif;
  transition: opacity 0.5s ease-in-out;
  opacity: ${props => props.faded ? 0 : 1};
`

const Span = styled.span`
  color: #999;
  transition: opacity 0.5s ease-in-out;
  opacity: ${props => props.faded ? 0 : 1};
`

const Btn = styled.img`
  cursor: pointer;
  margin-left: 15px;
  width: 16px;
  transition: opacity 0.5s ease-in-out;
  opacity: ${props => props.faded ? 0 : 1};
`