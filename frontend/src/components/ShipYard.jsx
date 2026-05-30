import { useState, useMemo, useCallback } from 'react'
import Board from './Board.jsx'

const SHIPS = [
  { name: 'carrier',    size: 5, label: 'Carrier'    },
  { name: 'battleship', size: 4, label: 'Battleship' },
  { name: 'cruiser',    size: 3, label: 'Cruiser'    },
  { name: 'submarine',  size: 3, label: 'Submarine'  },
  { name: 'destroyer',  size: 2, label: 'Destroyer'  },
]

function randomize() {
  const grid = Array(10).fill(null).map(() => Array(10).fill(false))
  const result = []
  for (const ship of SHIPS) {
    let placed = false
    for (let attempt = 0; attempt < 500 && !placed; attempt++) {
      const horizontal = Math.random() < 0.5
      const row = Math.floor(Math.random() * (horizontal ? 10 : 11 - ship.size))
      const col = Math.floor(Math.random() * (horizontal ? 11 - ship.size : 10))
      let valid = true
      const cells = []
      for (let i = 0; i < ship.size && valid; i++) {
        const r = horizontal ? row : row + i
        const c = horizontal ? col + i : col
        if (grid[r]?.[c]) valid = false
        else cells.push([r, c])
      }
      if (valid) {
        cells.forEach(([r, c]) => { grid[r][c] = true })
        result.push({ ...ship, row, col, horizontal })
        placed = true
      }
    }
    if (!placed) return randomize() // retry from scratch on rare collision
  }
  return result
}

export default function ShipYard({ onSubmit, onReady, confirmed, disabled }) {
  const [placements, setPlacements] = useState([])
  const [selected, setSelected]     = useState(SHIPS[0])
  const [horizontal, setHorizontal] = useState(true)
  const [hovered, setHovered]       = useState(null)

  const placedNames = useMemo(() => new Set(placements.map(p => p.name)), [placements])
  const allPlaced   = SHIPS.every(s => placedNames.has(s.name))

  const occupiedSet = useMemo(() => {
    const s = new Set()
    for (const p of placements) {
      for (let i = 0; i < p.size; i++) {
        const r = p.horizontal ? p.row : p.row + i
        const c = p.horizontal ? p.col + i : p.col
        s.add(`${r},${c}`)
      }
    }
    return s
  }, [placements])

  const preview = useMemo(() => {
    if (!hovered || !selected || placedNames.has(selected.name)) return null
    const { row, col } = hovered
    const cells = []
    let valid = true
    for (let i = 0; i < selected.size; i++) {
      const r = horizontal ? row : row + i
      const c = horizontal ? col + i : col
      if (r < 0 || r >= 10 || c < 0 || c >= 10 || occupiedSet.has(`${r},${c}`)) {
        valid = false; break
      }
      cells.push([r, c])
    }
    if (cells.length < selected.size) valid = false
    return { cells, valid }
  }, [hovered, selected, horizontal, occupiedSet, placedNames])

  const cells = useMemo(() => {
    const grid = Array(10).fill(null).map(() => Array(10).fill(null))
    for (const p of placements) {
      for (let i = 0; i < p.size; i++) {
        const r = p.horizontal ? p.row : p.row + i
        const c = p.horizontal ? p.col + i : p.col
        grid[r][c] = 'ship'
      }
    }
    if (preview) {
      const cls = preview.valid ? 'preview' : 'preview-invalid'
      for (const [r, c] of preview.cells) grid[r][c] = cls
    }
    return grid
  }, [placements, preview])

  const handleCellClick = useCallback((row, col) => {
    if (!selected || placedNames.has(selected.name) || !preview?.valid) return
    setPlacements(prev => [...prev, { ...selected, row, col, horizontal }])
    const next = SHIPS.find(s => !placedNames.has(s.name) && s.name !== selected.name)
    setSelected(next ?? null)
  }, [selected, placedNames, preview, horizontal])

  const handleHover = useCallback((r, c) => {
    setHovered(r !== null ? { row: r, col: c } : null)
  }, [])

  const handleRandomize = () => {
    setPlacements(randomize())
    setSelected(null)
  }

  const handleReset = () => {
    setPlacements([])
    setSelected(SHIPS[0])
  }

  const handleReady = () => {
    onSubmit(placements.map(({ name, row, col, horizontal }) => ({ name, row, col, horizontal })))
    onReady()
  }

  return (
    <div className="shipyard">
      <div className="shipyard-panel">
        <h3>Fleet</h3>
        {SHIPS.map(ship => (
          <div
            key={ship.name}
            className={[
              'ship-item',
              selected?.name === ship.name ? 'ship-selected' : '',
              placedNames.has(ship.name) ? 'ship-placed' : '',
              (disabled || confirmed) ? 'ship-disabled' : '',
            ].join(' ')}
            onClick={() => {
              if (!placedNames.has(ship.name) && !disabled && !confirmed) setSelected(ship)
            }}
          >
            <span>{ship.label} ({ship.size})</span>
            {placedNames.has(ship.name) && <span className="ship-check">✓</span>}
          </div>
        ))}

        <div className="orient-row">
          <button
            className="secondary"
            onClick={() => setHorizontal(h => !h)}
            disabled={disabled || confirmed}
          >
            {horizontal ? '→ Horizontal' : '↓ Vertical'}
          </button>
        </div>
        <div className="orient-row">
          <button className="secondary" onClick={handleRandomize} disabled={disabled || confirmed}>
            Randomize
          </button>
          <button className="secondary" onClick={handleReset} disabled={disabled || confirmed}>
            Reset
          </button>
        </div>

        {!confirmed ? (
          <button
            className="primary"
            disabled={!allPlaced || disabled}
            onClick={handleReady}
            style={{ marginTop: 8 }}
          >
            Ready
          </button>
        ) : (
          <p className="status-msg" style={{ marginTop: 8 }}>
            Waiting for opponent…
          </p>
        )}
      </div>

      <Board
        label="Place Your Ships"
        cells={cells}
        interactive={!confirmed && !disabled}
        onCellClick={handleCellClick}
        onCellHover={handleHover}
      />
    </div>
  )
}
