import React, { useState, useEffect } from 'react'
import ClipLoader from "react-spinners/ClipLoader"
import styled from '@emotion/styled'

import WS from 'webSocketService'


const CloudStatusComponent = (props) => {
  const OffComponent = (
    <CloudStatusWrapper faded={props.faded}>
      <Text>
        <Span>Start SorterBot Cloud</Span>
      </Text>
      <Btn
        onClick={props.startCloud}
        src={require('assets/start_white.svg')}
      />
    </CloudStatusWrapper>
  )

  const OnComponent = (
    <CloudStatusWrapper faded={props.faded}>
      <Text>
        <Span>SorterBot Cloud is running at: </Span>
        {props.cloudStatus}
      </Text>
      <Btn
        onClick={props.stopCloud}
        src={require('assets/stop_white.svg')}
      />
    </CloudStatusWrapper>
  )

  const LocalComponent = (
    <CloudStatusWrapper faded={props.faded}>
      <Text>
        <Span>SorterBot Cloud is running at</Span> localhost
      </Text>
    </CloudStatusWrapper>
  )

  const LoadingComponent = (props) => (
    <CloudStatusWrapper faded={props.faded}>
      <Text>
        <Span>{props.statusText}</Span>
      </Text>
      <ClipLoader
        css={{ marginLeft: 15 }}
        size={20}
        color={"#fff"}
        loading={true}
      />
    </CloudStatusWrapper>
  )

  switch (props.cloudStatus) {
    case 'startLoading':
      return <LoadingComponent statusText="SorterBot Cloud is starting..." />
    case 'stopLoading':
      return <LoadingComponent statusText="SorterBot Cloud is shutting down..." />
    case 'off':
      return OffComponent
    case 'loading':
      return <LoadingComponent statusText="Loading SorterBot status..." />
    default:
      if (props.cloudStatus) {
        return process.env.NODE_ENV === 'development' ? LocalComponent : OnComponent
      } else {
        return OffComponent
      }
  }
}

const HeaderComponent = () => {
  const [cloudStatus, setCloudStatus] = useState('loading')
  const [faded, setFaded] = useState(false)

  useEffect(()=>{
    WS.connect()
    WS.addCallbacks([
      { command: 'cloud_status', fn: (data) => fadeChangeStatus(data.cloudStatus) }
    ])
    WS.waitForSocketConnection(() => {
      WS.sendMessage({ command: 'fetch_cloud_status' })
    })
  }, [])

  const fadeChangeStatus = (newStatus) => {
    setFaded(true)
    setTimeout(() => {
      setCloudStatus(newStatus)
      setFaded(false)
    }, 500)
  }

  const startCloud = () => {
    WS.sendMessage({ command: 'start_cloud' })
    fadeChangeStatus('startLoading')
    localStorage.setItem('cloudStatus', 'startLoading')
  }

  const stopCloud = () => {
    WS.sendMessage({ command: 'stop_cloud' })
    fadeChangeStatus('stopLoading')
    localStorage.setItem('cloudStatus', 'stopLoading')
  }

  return (
    <Wrapper>
      <Header>
        <Logo src={require('assets/logo.png')} />
        <Right>
          <CloudStatusComponent
            faded={faded}
            cloudStatus={cloudStatus}
            startCloud={startCloud}
            stopCloud={stopCloud}
          />
          <Logout onClick={() => WS.sendMessage({ command: 'logout' })}>Logout</Logout>
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

const CloudStatusWrapper = styled.div`
  align-items: center;
  display: flex;
  flex-direction: row;
  transition: opacity 0.5s ease-in-out;
  opacity: ${props => props.faded ? 0 : 1};
`

const Logout = styled.button`
  text-transform: uppercase;
  background: none;
  color: #fff;
  font-size: 13px;
  line-height: 13px;
  font-weight: 600;
  position: relative;
  right: -10px;
  top: 1px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  & :active {
    color: #999;
  }
`