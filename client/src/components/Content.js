import React from 'react'
import styled from '@emotion/styled'
import { css } from '@emotion/core'
import PinchZoomPan from 'react-responsive-pinch-zoom-pan'


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

const ContentComponent = (props) => {
  return (
    <ContentContainer>
      <LogsContainer fadeOut={props.logs.length == 0}>
        {props.logs.map((log, i) => {
          const executionTime = props.logs[i - 1]?.created && (parseInt((log.created - props.logs[i - 1]?.created) * 1000) || '')
          return (
            <LogRow key={log.id} color={translateLogName(log.name).color}>
              <Time title={`Execution took ${executionTime}ms`}>{log.asctime.split(' ')[1]}   </Time>
              <Name title={log.name}>{translateLogName(log.name).name}:   </Name>
              <span title={`${log.pathname}:${log.lineno}`}>{log.msg}</span>
            </LogRow>
          )
        })}
      </LogsContainer>
      <ImageContainer fadeOut={props.logs.length !== 0 || !props.stitchUrl}>
        <PinchZoomPan
          zoomButtons={false}
          maxScale={2}
          position='center'
          style={{ display: 'flex', alignItems: 'center' }}
        >
          <img alt='' src={props.stitchUrl}/>
        </PinchZoomPan>
      </ImageContainer>
    </ContentContainer>
  )
}

export default ContentComponent


const ContentContainer = styled.div`
  width: 100%;
  position: relative;
`

const LogsContainer = styled.div(props => css`
  background: ${props.theme.colors.dark};
  flex: 1;
  margin: 15px;
  padding: 15px;
  overflow-y: auto;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transition: all 0.3s ease-in-out;
  opacity: ${props.fadeOut ? 0 : 1};
  z-index: 50;
`)

const ImageContainer = styled.div(props => css`
  background: #000;
  z-index: ${props.fadeOut ? 0 : 100};
  display: flex;
  align-items: center;
  margin: 15px;
  padding: 15px;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transition: all 0.3s ease-in-out;
  opacity: ${props.fadeOut ? 0 : 1};
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

