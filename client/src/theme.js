import { css } from '@emotion/core'

export default {
  colors: {
    primary: '#30b90e',
    darkPrimary: '#115201',
    pressed: '#fafafa',
    dark: '#2e2e2e'
  },
  shadow: (shadowType) => {
    // { layers: 5, maxDist: 2.5, maxBlur: 3, maxOpacity: 0.12, isInset: false, reverseOpacity: false }
    let layers, maxDist, maxBlur, maxOpacity, isInset, reverseOpacity
    if (typeof shadowType === 'string') {
      switch (shadowType) {
        case 'box':
          layers = 5; maxDist = 50; maxBlur = 100; maxOpacity = 0.08; isInset = false; reverseOpacity = true
          break
        case 'innerBox':
          layers = 5; maxDist = 2.5; maxBlur = 3; maxOpacity = 0.12; isInset = false; reverseOpacity = false
          break
        case 'innerBoxInset':
          layers = 5; maxDist = 0; maxBlur = 3; maxOpacity = 0.12; isInset = true; reverseOpacity = false
          break
        case 'button':
          layers = 5; maxDist = 2; maxBlur = 2; maxOpacity = 0.07; isInset = false; reverseOpacity = false
          break
        case 'buttonInset':
          layers = 5; maxDist = 0; maxBlur = 3; maxOpacity = 0.1; isInset = true; reverseOpacity = false
          break
        default:
          break
      }
    } else {
      ({ layers, maxDist, maxBlur, maxOpacity, isInset, reverseOpacity } = shadowType)
    }
    const x_max = 8
    let shadows = 'box-shadow: '
    for (let l = 1; l <= layers; l++) {
      const x = x_max * l / layers
      const opacityFn = n => 2.98e-4 * Math.pow(n, 3) - 3.46e-3 * Math.pow(n, 2) + 0.0181 * n + 3.71e-3
      const maxOpacityFn = opacityFn(x_max)
      const opacity = parseFloat(maxOpacity * opacityFn(reverseOpacity ? x_max - x + 1 : x) / maxOpacityFn).toFixed(4)

      const distAndBlurFn = n => 0.0372 * Math.pow(Math.E, 0.488 * n)
      const maxDistAndBlurFn = distAndBlurFn(x_max)
      const dist = parseFloat(maxDist * distAndBlurFn(x) / maxDistAndBlurFn).toFixed(4)
      const blur = parseFloat(maxBlur * distAndBlurFn(x) / maxDistAndBlurFn).toFixed(4)

      shadows += `${isInset ? 'inset ' : ''}0 ${dist}px ${blur}px rgba(40, 40, 40, ${opacity})`
      if (l !== layers) shadows += ', '
    }
    shadows += ';'

    return shadows
  },
  borders: {
    base: css`border: 1px solid rgba(230, 230, 230, 1);`,
    invisible: css`border: 1px solid rgba(40, 40, 40, 0);`,
  }
}