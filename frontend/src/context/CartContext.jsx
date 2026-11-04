import { createContext, useContext, useState, useEffect } from 'react'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    try {
      const saved = localStorage.getItem('cart')
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(items))
  }, [items])

  const addItem = (product, quantity = 1) => {
    setItems(prev => {
      const existing = prev.find(i => i.id === product.id)
      const currentQty = existing ? existing.qty : 0
      
      if (product.stock !== undefined && currentQty + quantity > product.stock) {
        return prev 
      }

      if (existing) {
        return prev.map(i => 
          i.id === product.id ? { ...i, qty: i.qty + quantity } : i
        )
      }
      return [...prev, { ...product, qty: quantity }]
    })
  }

  const removeItem = (id) => setItems(prev => prev.filter(i => i.id !== id))

  const updateQuantity = (id, newQty) => {
    if (newQty <= 0) return removeItem(id)
    setItems(prev => 
      prev.map(i => i.id === id ? { ...i, qty: newQty } : i)
    )
  }

  const clear = () => setItems([])

  const total = items.reduce((sum, item) => sum + (Number(item.price) || 0) * item.qty, 0)
  const count = items.reduce((sum, item) => sum + item.qty, 0)

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, updateQuantity, clear, total, count }}>
      {children}
    </CartContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}