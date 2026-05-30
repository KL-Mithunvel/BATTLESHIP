import './Board.css'

const COLS = ['A','B','C','D','E','F','G','H','I','J']

const STATE_CLASS = {
  ship:            'cell-ship',
  hit:             'cell-hit',
  miss:            'cell-miss',
  preview:         'cell-preview',
  'preview-invalid': 'cell-preview-invalid',
}

export default function Board({ label, cells, onCellClick, onCellHover, interactive = false }) {
  return (
    <div className="board-wrap">
      <div className="board-label">{label}</div>
      <div className="board-grid">
        <div className="board-corner" />
        {COLS.map(c => <div key={c} className="board-col-header">{c}</div>)}

        {cells.map((row, r) => (
          <Row
            key={r}
            rowIndex={r}
            cells={row}
            interactive={interactive}
            onCellClick={onCellClick}
            onCellHover={onCellHover}
          />
        ))}
      </div>
    </div>
  )
}

function Row({ rowIndex, cells, interactive, onCellClick, onCellHover }) {
  return (
    <>
      <div className="board-row-header">{rowIndex + 1}</div>
      {cells.map((state, c) => (
        <div
          key={c}
          className={`board-cell ${STATE_CLASS[state] ?? 'cell-empty'} ${interactive ? 'interactive' : ''}`}
          onClick={() => interactive && onCellClick?.(rowIndex, c)}
          onMouseEnter={() => interactive && onCellHover?.(rowIndex, c)}
          onMouseLeave={() => interactive && onCellHover?.(null, null)}
        />
      ))}
    </>
  )
}
