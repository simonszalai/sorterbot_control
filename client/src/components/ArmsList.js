import React, { useState, useEffect } from 'react'
import { css } from '@emotion/core'
import styled from '@emotion/styled'
import Fade from 'react-reveal/Fade'
import WS from 'webSocketService'


const ArmsListComponent = (props) => {
  const [selected, setSelected] = useState(null)
  const [arms, setArms] = useState([])
  const [blinkingArms, setBlinkingArms] = useState({})

  useEffect(() => {
    const initWebSocket = async () => {
      await WS.connect()
      WS.addCallbacks([
        { command: 'fetch_arms', fn: setArms },
        { command: 'arm_conn_status', fn: ArmConnStatusCallback },
      ])
      WS.fetchArms()
    }
    initWebSocket()
  }, [])

  const ArmConnStatusCallback = (armId, armConnStatus) => {
    setBlinkingArms({ ...blinkingArms, [armId]: armConnStatus ? 'ok' : 'dc' })
    setTimeout(() => {
      setBlinkingArms({ ...blinkingArms, [armId]: false })
    }, 3000)
  }

  return (
    <ArmsList>
      <Fade cascade duration={500} distance="3px">
        <div>
          {arms.map(arm => {
            return (
            <Arm
              selected={selected}
              onClick={() => setSelected(arm.id)}
              key={arm.arm_id}
            >
              <div>
                <ArmId>{arm.arm_id}</ArmId>
                <LastOnline>{arm.last_online}</LastOnline>
              </div>
              <Buttons>
                  <StartBtn src={require(`assets/start.svg`)} onClick={() => WS.startSession(arm.arm_id)} />
                <Status selected={selected} blink={blinkingArms[arm.arm_id]} />
              </Buttons>
              <Border selected={selected} />
            </Arm>
          )})}
        </div>
      </Fade>
    </ArmsList>
  )
}

export default ArmsListComponent



const ArmsList = styled.div`
  background-color: #fff;
  flex: 0 0 auto;
  overflow: auto;
  padding: 30px 15px;
  width: 280px;
`

const armSelected = props => css`
  background-color: ${props.theme.colors.primary};
  color: #fff;
  border-color: ${props.theme.colors.primary}
`

const Arm = styled.div(props => css`
  align-items: center;
  background-color: #fff;
  border-radius: 4px;
  color: #333;
  cursor: pointer;
  display: flex;
  height: 70px;
  justify-content: space-between;
  margin-bottom: 19px;
  overflow: hidden;
  padding: 13px;
  padding-right: 17px;
  position: relative;
  transition: all 0.3s ease-in-out;
  ${props.theme.borders.base}
  ${props.theme.shadow('innerBox')}
  ${props.selected ? armSelected(props) : ''}
  & :hover {
    box-shadow: none;
  }
  & :active {
    background-color: ${props.selected ? props.theme.colors.darkPrimary : props.theme.colors.pressed};
    ${props.theme.shadow('innerBoxInset')}
  }
`)

const ArmId = styled.div`
  font-family: Lato, sans-serif;
  font-weight: 700;
  position: relative;
  z-index: 10;
`

const LastOnline = styled.div`
  font-family: Tahoma, Verdana, Segoe, sans-serif;
  font-size: 11px;
  line-height: 13px;
`

const Buttons = styled.div`
  display: flex;
  flex: 0 0 auto;
`

const StartBtn = styled.img`
  width: 18px;
  height: 18px;
  cursor: pointer;
`

const Status = styled.div(props => css`
  // background-color: ${props.selected ? props.theme.colors.darkPrimary : props.theme.colors.primary};
  background-color: #bbb;
  ${props.blink === 'ok' ? `background-color: ${props.theme.colors.primary};` : ''}
  ${props.blink === 'dc' ? `background-color: ${props.theme.colors.warning};` : ''}
  border-radius: 100px;
  box-shadow: inset 0 0 3px 0 rgba(51, 51, 51, 0.48);
  height: 18px;
  margin-left: 9px;
  min-height: 18px;
  min-width: 18px;
  width: 18px;
  transition: all 0.15s ease-in-out;
  ${props.blink ? 'animation: 3s ease-out blink' : ''};
  @keyframes blink {
    from {
      background-color: #bbb;
    }
  
    10% {
      ${props.blink === 'ok' ? `background-color: ${props.theme.colors.primary};` : ''}
      ${props.blink === 'dc' ? `background-color: ${props.theme.colors.warning};` : ''}
    }
  
    to {
      background-color: #bbb;
    }
  }
`)

const Border = styled.div`
  background-color: ${props => props.selected ? props.theme.colors.darkPrimary : props.theme.colors.primary};
  bottom: 0%;
  height: 100%;
  left: 0%;
  position: absolute;
  right: auto;
  top: 0%;
  width: 4px;
  z-index: 100;
  transition: all 0.15s ease-in-out;
`
