import React, { useState, useEffect } from 'react'
import styled from '@emotion/styled'
import { css } from '@emotion/core'
import WS from 'webSocketService'


const translateLogName = (logName) => {
  switch (logName) {
    case 'SORTERBOT_CLOUD':
      return {
        name: 'SBC',
        color: '#94fdff'
      }
    case 'SORTERBOT_RASPBERRY':
      return {
        name: 'SBR',
        color: '#ff5496'
      }
    default:
      throw new Error('Log Provider unknown!')
  }
}

const LogsComponent = (props) => {
  if (props.logs.length > 0) {
    return (
      <LogsContainer>
        {props.logs.map((log, i) => {
          const executionTime = parseInt((props.logs[i + 1]?.created - log.created) * 1000) || ''
          return (
            <LogRow key={log.id} color={translateLogName(log.name).color}>
              <Time title={`Execution took ${executionTime}ms`}>{log.asctime}   </Time>
              <Name title={log.name}>{translateLogName(log.name).name}:   </Name>
              <span title={`${log.pathname}:${log.lineno}`}>{log.msg}</span>
            </LogRow>
          )
        })}
      </LogsContainer>
    )
  } else {
    return null
  }
}

export default LogsComponent


const LogsContainer = styled.div(props => css`
  background: ${props.theme.colors.dark};
  flex: 1;
  margin: 15px;
  padding: 15px;
  overflow-y: auto;
`)

const LogRow = styled.div(props => css`
  font-family: Ubuntu, Arial, sans-serif;
  font-size: 13px;
  color: ${props.color};
  line-height: 17px;
`)

const Time = styled.span`
  opacity: 0.7;
`

const Name = styled.span`
  font-weight: 700;
`

