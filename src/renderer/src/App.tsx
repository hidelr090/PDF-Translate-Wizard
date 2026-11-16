export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900">PDF Translate Wizard</h1>
        <p className="text-sm text-gray-500">Tradutore de PDF com preservação de layout</p>
      </header>

      <main className="max-w-4xl mx-auto py-8 px-6">
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Bem-vindo</h2>
          <p className="text-gray-600">
            Selecione um PDF para começar a tradução. Os recursos de processamento
            de documento, integração com IA e reconstrução de layout serão
            disponibilizados nas próximas fases de implementação.
          </p>
        </section>
      </main>
    </div>
  );
}