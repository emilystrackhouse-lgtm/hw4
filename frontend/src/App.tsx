import { Route, Routes } from 'react-router'
import AuthProvider from './components/AuthProvider.tsx'
import Layout from './components/Layout.tsx'
import About from './pages/About.tsx'
import Account from './pages/Account.tsx'
import CreateAccount from './pages/CreateAccount.tsx'
import Home from './pages/Home.tsx'
import Login from './pages/Login.tsx'
import NotFound from './pages/NotFound.tsx'
import ProductDetail from './pages/ProductDetail.tsx'
import Products from './pages/Products.tsx'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="products" element={<Products />} />
          <Route path="products/:productId" element={<ProductDetail />} />
          <Route path="about" element={<About />} />
          <Route path="login" element={<Login />} />
          <Route path="create-account" element={<CreateAccount />} />
          <Route path="account" element={<Account />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
