export function resolveImageUrl(image, fallback = null) {
  if (!image) return fallback

  // صورة Vite محلية (ناتجة عن import — تكون object أو string)
  if (typeof image !== 'string') return image

  // رابط كامل أو data URI
  if (
    image.startsWith('http://') ||
    image.startsWith('https://') ||
    image.startsWith('data:')
  ) {
    return image
  }

  // مسار ميديا من Django مثل /media/products/bike.jpg
  if (image.startsWith('/media/')) {
    // BASE_URL في axios هو http://localhost:8000/api
    // نستخرج الأصل: http://localhost:8000
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
    const origin = apiUrl.replace(/\/api\/?$/, '')
    return `${origin}${image}`
  }

  // مسار نسبي لـ Vite (src/assets)
  return image
}