import { Routes, Route } from 'react-router-dom'
import Home from '../pages/Home'
import Shop from '../pages/Shop'
import About from '../pages/About'
import News from '../pages/News'
import Contact from '../pages/Contact'
import Login from '../pages/Login'
import Register from '../pages/Register' // <-- استيراد الصفحة الجديدة
import AdminDashboard from '../pages/AdminDashboard'
import NotFound from '../pages/NotFound'
import PrivateRoute from './PrivateRoute'
import CustomerRoute from './CustomerRoute'

import ProductDetail from '../pages/ProductDetail'
import Checkout from '../pages/Checkout'
import OrderStatus from '../pages/OrderStatus'


import Cart from '../pages/Cart'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} /> {/* <-- إضافة المسار */}
      
      <Route path="/home" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/cycle" element={<Shop />} />
      <Route path="/shop" element={<Shop />} />
      <Route path="/product/:id" element={<ProductDetail />} />
      <Route path="/news" element={<News />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/cart" element={<Cart />} />
      <Route path="/checkout" element={<CustomerRoute><Checkout /></CustomerRoute>} />
      <Route path="/orders" element={<CustomerRoute><OrderStatus /></CustomerRoute>} />
      <Route path="/admin" element={<PrivateRoute><AdminDashboard /></PrivateRoute>} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}