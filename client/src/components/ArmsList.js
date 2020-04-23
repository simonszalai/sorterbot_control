import React, { useState, useEffect } from 'react'
import moment from 'moment'
import { css } from '@emotion/core'
import styled from '@emotion/styled'
import Fade from 'react-reveal/Fade'
import WS from 'webSocketService'


const ArmsListComponent = (props) => {
  const [arms, setArms] = useState([])
  const [blinkingArms, setBlinkingArms] = useState({})

  useEffect(() => {
    WS.connect()
    WS.addCallbacks([
      { command: 'fetch_arms', fn: (data) => setArms(data.arms) },
      { command: 'arm_conn_status', fn: (data) => ArmConnStatusCallback(data.armId, data.cloudConnectSuccess) },
    ])
    WS.waitForSocketConnection(() => {
        WS.sendMessage({ command: 'fetch_arms' })
    })
  }, [])

  const ArmConnStatusCallback = (armId, armConnStatus) => {
    setBlinkingArms({ ...blinkingArms, [armId]: armConnStatus ? 'ok' : 'dc' })
    setTimeout(() => {
      setBlinkingArms({ ...blinkingArms, [armId]: false })
    }, 3000)
  }

  const onArmClick = (armId) => {
    props.setSelectedArm(armId)
    WS.sendMessage({ command: 'fetch_sessions_of_arm', armId })
    WS.sendMessage({ command: 'set_open_logs', open_logs: 'none' })
  }

  const onStartSession = (e, armId) => {
    e.stopPropagation()
    e.preventDefault();
    WS.sendMessage({ command: 'start_session', armId })
  }

  return (
    <ArmsList>
      <Fade cascade duration={500} distance="3px">
        <div>
          {arms.map(arm => {
            return (
              <Arm
                selected={props.selectedArm === arm.arm_id}
                onClick={() => onArmClick(arm.arm_id)}
                key={arm.arm_id}
              >
                <ArmInnerWrapper>
                  <div>
                    <ArmId>{arm.arm_id}</ArmId>
                    <LastOnline>{moment(arm.last_online).local().format('YYYY-MM-DD HH:mm:ss')}</LastOnline>
                  </div>
                  <Buttons>
                      <StartBtn src={require(`assets/start.svg`)} onClick={(e) => onStartSession(e, arm.arm_id)} />
                    <Status selected={props.selectedArm === arm.arm_id} blink={blinkingArms[arm.arm_id]} />
                  </Buttons>
                </ArmInnerWrapper>
              </Arm>
            )
          })}
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

const ArmInnerWrapper = styled.div`
  align-items: center;
  display: flex;
  justify-content: space-between;
  padding: 13px;
  padding-right: 17px;
  transition: all 0.3s ease-in-out;
  width: 245px;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
`

const Arm = styled.div(props => css`
  background-color: #fff;
  border-radius: 4px;
  color: #333;
  cursor: pointer;
  display: flex;
  height: 70px;
  margin-bottom: 19px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease-in-out;
  ${props.theme.borders.base}
  ${props.selected && `border-left: 4px solid ${props.theme.colors.primary};`}
  ${props.theme.shadow('innerBox')}
  & :hover {
    box-shadow: none;
  }
  & :active {
    background-color: ${props.theme.colors.pressed};
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
  opacity: 0.7;
  transition: all 0.3s ease-in-out;
  & :hover {
    transform: scale(1.2);
  }
  & :active {
    opacity: 1;
    transform: scale(1.1);
  }
`

const Status = styled.div(props => css`
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
