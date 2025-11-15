import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Eidos
          </h1>
          <p className="text-2xl text-gray-600 mb-8">
            Ваш персональный ИИ-ассистент
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/register"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Начать бесплатно
            </Link>
            <Link
              href="/login"
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Войти
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
