import React, { useState, useEffect } from 'react'
import styled from '@emotion/styled'
import { css } from '@emotion/core'
import Fade from 'react-reveal/Fade'
import WS from 'webSocketService'


const SessionsListComponent = (props) => {
  const [sessions, setSessions] = useState([])
  const [selected, setSelected] = useState([])
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    WS.connect()
    WS.addCallbacks([
      { command: 'fetch_sessions_of_arm', fn: (data) => setSessions(data.sessions) },
    ])
    WS.waitForSocketConnection(() => {
        WS.sendMessage({ command: 'fetch_arms' })
    })
  }, [])

  const onButtonClick = (e, label, session) => {
    e.stopPropagation()
    setSelected([session.id, label])
    WS.sendMessage({
      command: 'fetch_logs',
      arm_id: props.selectedArm,
      sess_id: session.id,
      log_type: label
    })
    WS.sendMessage({
      command: 'set_open_logs',
      open_logs: `${props.selectedArm}.${session.id}.${label}`
    })
  }

  const onSessionClick = (expandedId, sessionId, setExpandedId) => {
    const newExpanded = expandedId === sessionId ? null : sessionId
    setExpandedId(newExpanded)
    if (!newExpanded) setSelected([])
  }
  
  const createButton = (label, session) => {
    const disabled = !session.enabled_log_types?.split(',').includes(label.toString())
    return (
      <Btn
        key={label}
        onClick={(e) => onButtonClick(e, label, session)}
        selected={selected[0] === session.id && selected[1] === label}
        disabled={disabled}
      >
        {label}
      </Btn>
    )
  }

  return (
    <SessionsList>
      <Fade cascade duration={500} distance="3px">
        <div>
          {sessions.map(session => (
            <Session onClick={() => onSessionClick(expandedId, session.id, setExpandedId)} key={session.id}>
              <Header isExpanded={expandedId === session.id}>
                <div>
                  <SessionId>Session ID</SessionId>
                  <StartTime>{session.session_id}</StartTime>
                </div>
                <Status>{session.status}</Status>
                <Dropdown
                  isExpanded={expandedId === session.id}
                  src={require('assets/dropdown.svg')}
                />
              </Header>
              <Body isExpanded={expandedId === session.id}>
                <BodyInner>
                  <SectionTitle>Images</SectionTitle>
                  <BtnWrapper>
                    {createButton('Before', session)}
                    {createButton('After', session)}
                  </BtnWrapper>
                  <SectionTitle>Logs</SectionTitle>
                  <BtnWrapper>
                    {session.log_filenames.split(",").map(label => createButton(label, session))}
                  </BtnWrapper>
                  <BtnWrapper>
                    {createButton('Command Generation', session)}
                  </BtnWrapper>
                </BodyInner>
              </Body>
            </Session>
          ))}
        </div>
      </Fade>
    </SessionsList>
  )
}

export default SessionsListComponent



const SessionsList = styled.div`
  flex: 0 0 auto;
  overflow: auto;
  padding: 15px;
  position: relative;
  width: 300px;
  z-index: 10;
`

const Session = styled.div(props => css`
  align-items: center;
  background-color: #f8f8f8;
  background-image: linear-gradient(135deg, #fafafa, #eee);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  overflow: hidden;
  flex-direction: column;
  justify-content: flex-start;
  margin: 15px 0;
  position: relative;
  ${props.theme.borders.base}
  ${props.theme.shadow('innerBox')}
  transition: all 0.3s ease-in-out;
  & :hover {
    box-shadow: none;
  }
`)

const Header = styled.div(props => css`
  background-color: #fff;
  border-bottom: 1px solid rgba(0, 0, 0, ${props.isExpanded ? 0.12 : 0});
  border-radius: 4px 4px 0px 0px;
  display: flex;
  flex: 0 0 auto;
  justify-content: space-between;
  height: 68px;
  overflow: hidden;
  padding: 15px 15px 10px;
  position: relative;
  width: 100%;
  transition: all 0.3s ease-in-out;
  transition: border-bottom 0.2s ease ${props.isExpanded ? '0s' : '0.4s'};
`)

const Dropdown = styled.img`
  bottom: 9px;
  height: 13px;
  left: auto;
  opacity: 0.47;
  position: absolute;
  right: 12px;
  top: auto;
  width: 13px;
  transition: all 0.3s ease-in-out;
  ${props => props.isExpanded && 'transform: rotateZ(180deg);'}
`

const SessionId = styled.div`
  font-family: Ubuntu, Helvetica, sans-serif;
  font-size: 17px;
  line-height: 18px;
  margin-bottom: 6px;
  margin-top: 0px;
`

const StartTime = styled.div`
  font-family: Lato, sans-serif;
  font-size: 13px;
`

const Status = styled.div`
  align-items: center;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #10a019;
  bottom: auto;
  box-shadow: none;
  color: #10a019;
  display: flex;
  flex: 0 0 auto;
  font-family: Montserrat, sans-serif;
  font-size: 10px;
  font-weight: 600;
  justify-content: center;
  left: auto;
  line-height: 10px;
  padding: 4px 7px 2px;
  position: absolute;
  right: 11px;
  text-transform: uppercase;
  top: 15px;
`

const expandedBody = () => css`
  max-height: 300px;
`

const Body = styled.div`
  width: 100%;
  overflow: hidden;
  max-height: 0;
  padding: 0 10px;
  transition: max-height 0.6s ease;
  ${props => props.isExpanded && expandedBody()}
`

const BodyInner = styled.div`
  padding: 10px 0;
`

const SectionTitle = styled.div`
  font-family: Ubuntu, Helvetica, sans-serif;
  font-size: 18px;
  line-height: 18px;
  margin: 10px 5px 15px;
`

const BtnWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  width: 100%;
`

const btnSelected = (props) => css`
  color: #fff;
  background-color: ${props.theme.colors.primary};
  border-color: ${props.theme.colors.primary};
`

const Btn = styled.button(props => css`
  align-items: center;
  background-color: ${props.disabled ? 'transparent' : '#fff'};
  border-radius: 3px;
  color: ${props.disabled ? '#aaa' : '#333'};
  ${!props.disabled && 'cursor: pointer;'}
  display: flex;
  flex: 1;
  font-family: Montserrat, sans-serif;
  font-size: 12px;
  font-weight: 600;
  height: 28px;
  margin: 0 2.5px 5px;
  justify-content: center;
  padding: 0 4px;
  text-transform: uppercase;
  transition: all 0.15s ease-in-out;
  ${props.disabled ? props.theme.borders.darker : props.theme.borders.base}
  ${!props.disabled && props.theme.shadow('button')}
  ${props.selected && btnSelected(props)}
  & :hover {
    box-shadow: none;
  }
  & :active {
    background-color: ${props.theme.colors.pressed};
    color: #555;
    ${props.theme.shadow('buttonInset')}
    ${props.theme.borders.base}
  }
`)