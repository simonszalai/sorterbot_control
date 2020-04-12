import React, { useState } from 'react'
import { css } from '@emotion/core'
import styled from '@emotion/styled'


const ArmComponent = (props) => {
  const selected = props.selected === props.arm.id
  return (
    <Arm selected={selected} onClick={props.onClick}>
      <div>
        <ArmId>{props.arm.id}</ArmId>
        <Address>{props.arm.address}</Address>
      </div>
      <Buttons>
        <StartBtn src={require(`assets/start.svg`)} />
        <Status selected={selected} />
      </Buttons>
      <Border selected={selected} />
    </Arm>
  )
}

const ArmsListComponent = () => {
  const [selected, setSelected] = useState(null)

  const arms = [{
    id: 'ARM001',
    address: 'https://dizzying-woodcock-7809.dataplicity.io'
  },{
    id: 'ARM002',
    address: 'https://dizzying-woodcock-7809.dataplicity.io'
  },{
    id: 'ARM003',
    address: 'https://dizzying-woodcock-7809.dataplicity.io'
  }]
  return (
    <ArmsList>
      {arms.map(arm => (
        <ArmComponent
          key={arm.id}
          arm={arm}
          selected={selected}
          onClick={() => setSelected(arm.id)}
        />)
      )}
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

const Address = styled.div`
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
`

const armStatusSelected = (props) => css`
  background-color: ${props.theme.colors.darkPrimary};
`

const Status = styled.div(props => css`
  background-color: ${props.selected ? props.theme.colors.darkPrimary : props.theme.colors.primary};
  border-radius: 100px;
  box-shadow: inset 0 0 3px 0 rgba(51, 51, 51, 0.48);
  height: 18px;
  margin-left: 9px;
  min-height: 18px;
  min-width: 18px;
  width: 18px;
  transition: all 0.15s ease-in-out;
  animation: 3s linear infinite blink;
  @keyframes blink {
    from {
      background-color: #fff;
    }
  
    10% {
      background-color: ${props.selected ? props.theme.colors.darkPrimary : props.theme.colors.primary};
    }
  
    to {
      background-color: #fff;
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