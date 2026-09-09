import { useId, useState } from 'react'
import {
  FloatingArrow,
  FloatingFocusManager,
  FloatingPortal,
  arrow,
  autoUpdate,
  flip,
  hide,
  offset,
  shift,
  useDismiss,
  useFloating,
  useInteractions,
  useRole,
} from '@floating-ui/react'
import './BalaoMascote.css'

function BalaoMascote({
  target,
  open = false,
  standalone = false,
  text,
  imageSrc,
  imageFit = 'contain',
  imagePosition = 'center bottom',
  placement = 'top',
  onNext,
  onClose,
  closeLabel = 'Fechar tutorial',
  showCloseButton = true,
  nextLabel = 'Próximo passo',
  children,
  className = '',
  dialogLabel = 'Guia de primeiro acesso',
  focusOnOpen = false,
}) {
  const [arrowElement, setArrowElement] = useState(null)
  const descriptionId = useId()
  const {
    refs: { setFloating },
    floatingStyles,
    context,
    middlewareData,
    isPositioned,
  } = useFloating({
    open: open && Boolean(target) && !standalone,
    onOpenChange: (nextOpen) => { if (!nextOpen) onClose?.() },
    elements: { reference: target },
    placement,
    strategy: 'fixed',
    whileElementsMounted: autoUpdate,
    middleware: [
      offset(32),
      flip({ padding: 12, fallbackAxisSideDirection: 'start' }),
      shift({ padding: 24 }),
      arrow({ element: arrowElement, padding: 34 }),
      hide({ strategy: 'referenceHidden' }),
    ],
  })
  const dismiss = useDismiss(context, { outsidePress: false })
  const role = useRole(context, { role: 'dialog' })
  const { getFloatingProps } = useInteractions([dismiss, role])

  if (!open || (!target && !standalone)) return null

  const invisible = !standalone && (!isPositioned || middlewareData.hide?.referenceHidden)

  return (
    <FloatingPortal>
      <FloatingFocusManager
        context={context}
        modal={false}
        initialFocus={focusOnOpen ? 0 : -1}
        returnFocus={focusOnOpen}
        closeOnFocusOut={false}
      >
        <section
          ref={setFloating}
          {...getFloatingProps({
            className: `mascot-tip${standalone ? ' mascot-tip--standalone' : ''} ${className}`,
            style: {
              ...(standalone ? {} : floatingStyles),
              visibility: invisible ? 'hidden' : 'visible',
            },
            'aria-label': dialogLabel,
            'aria-describedby': descriptionId,
          })}
        >
          {!standalone && (
            <FloatingArrow
              ref={setArrowElement}
              context={context}
              width={30}
              height={15}
              tipRadius={2}
              fill="var(--mascot-tip-background, white)"
            />
          )}

          <div className="mascot-tip__layout">
            <div className="mascot-tip__content">
              <p id={descriptionId} className="mascot-tip__text" aria-live="polite" aria-atomic="true">
                {text}
              </p>
              {children}
              {(onNext || (onClose && showCloseButton)) && <div className="mascot-tip__controls">
                {onNext && (
                  <button type="button" className="mascot-tip__next" aria-label={nextLabel} onClick={onNext}>
                    Continuar
                  </button>
                )}
                {onClose && showCloseButton && (
                  <button type="button" className="mascot-tip__close" aria-label={closeLabel} onClick={onClose}>
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" /></svg>
                  </button>
                )}
              </div>}
            </div>

            {imageSrc && (
              <div className="mascot-tip__portrait" aria-hidden="true">
                <img
                  key={imageSrc}
                  src={imageSrc}
                  alt=""
                  style={{ objectFit: imageFit, objectPosition: imagePosition }}
                />
              </div>
            )}
          </div>
        </section>
      </FloatingFocusManager>
    </FloatingPortal>
  )
}

export default BalaoMascote
