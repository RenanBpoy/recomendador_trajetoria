import { createContext, useContext } from 'react'

export const FirstAccessGuideContext = createContext(null)

const emptyTargetRef = () => {}
const emptyGuideAction = () => false

export function useFirstAccessGuideTarget(targetId) {
  const context = useContext(FirstAccessGuideContext)
  return context?.getTargetRef(targetId) || emptyTargetRef
}

export function useFirstAccessGuideAction() {
  const context = useContext(FirstAccessGuideContext)
  return context?.completeGuideAction || emptyGuideAction
}
