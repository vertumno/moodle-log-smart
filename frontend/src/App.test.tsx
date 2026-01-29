import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App Integration', () => {
  it('renders title and initial state', () => {
    render(<App />)

    // Verifica título
    expect(screen.getByText(/MoodleLogSmart/i)).toBeInTheDocument()

    // Verifica subtítulo
    expect(screen.getByText(/Transforme seus logs do Moodle/i)).toBeInTheDocument()

    // Verifica footer
    expect(screen.getByText(/Zero configuração necessária/i)).toBeInTheDocument()

    // Verifica que UploadZone está visível no estado inicial
    expect(screen.getByText(/Arraste seu CSV aqui ou clique/i)).toBeInTheDocument()
  })

  it('has all required states defined', () => {
    const { container } = render(<App />)

    // Verifica que o componente renderizou
    expect(container).toBeTruthy()

    // Verifica classes Tailwind aplicadas
    const mainContainer = container.querySelector('.min-h-screen')
    expect(mainContainer).toBeInTheDocument()
    expect(mainContainer).toHaveClass('bg-gray-50')
  })

  it('renders card with correct styling', () => {
    const { container } = render(<App />)

    // Verifica card principal
    const card = container.querySelector('.bg-white')
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('rounded-lg', 'shadow-lg')
  })

  it('has responsive design classes', () => {
    const { container } = render(<App />)

    const mainContainer = container.querySelector('.min-h-screen')
    expect(mainContainer).toHaveClass('flex', 'flex-col', 'items-center', 'justify-center')

    // Verifica padding responsivo
    expect(mainContainer).toHaveClass('p-4')
  })
})
