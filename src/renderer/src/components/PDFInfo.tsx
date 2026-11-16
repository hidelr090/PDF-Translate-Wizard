interface PDFInfoProps {
  document: any;
  classification: any;
  loading: boolean;
  error: string | null;
}

export default function PDFInfo({
  document,
  classification,
  loading,
  error,
}: PDFInfoProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <span className="ml-3 text-gray-600">Processando PDF...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700">
        <h3 className="font-medium">Erro ao processar PDF</h3>
        <p className="mt-1 text-sm">{error}</p>
      </div>
    );
  }

  if (!document) {
    return null;
  }

  const totalBlocks = document.pages.reduce(
    (acc: number, p: any) => acc + p.textBlocks.length,
    0
  );
  const totalTables = document.pages.reduce(
    (acc: number, p: any) => acc + p.tables.length,
    0
  );
  const totalImages = document.pages.reduce(
    (acc: number, p: any) => acc + p.images.length,
    0
  );

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            📄 {document.filePath.split("/").pop() || document.filePath.split("\\").pop()}
          </h2>
          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs font-medium text-gray-500 uppercase">Páginas</p>
              <p className="font-medium">{document.totalPages}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs font-medium text-gray-500 uppercase">Orientação</p>
              <p className="font-medium">
                {document.pages[0]?.orientation === "landscape"
                  ? "Paisagem"
                  : "Retrato"}
              </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs font-medium text-gray-500 uppercase">Blocos de texto</p>
              <p className="font-medium">{totalBlocks}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs font-medium text-gray-500 uppercase">Tabelas</p>
              <p className="font-medium">{totalTables}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs font-medium text-gray-500 uppercase">Imagens</p>
              <p className="font-medium">{totalImages}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs font-medium text-gray-500 uppercase">Texto selecionável</p>
              <p className="font-medium">
                {document.pages.every((p: any) => p.hasExtractableText)
                  ? "Sim"
                  : "Não (OCR necessário)"}
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            🔍 Classificação
          </h2>
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <p className="text-xs font-medium text-gray-500 uppercase mb-1">
              Tipo de documento
            </p>
            <p className="font-medium capitalize">
              {classification?.documentType || "N/A"}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <p className="text-xs font-medium text-gray-500 uppercase mb-1">
              Estratégia recomendada
            </p>
            <p className="font-medium">
              Estratégia {classification?.recommendedStrategy || "A"}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-xs font-medium text-gray-500 uppercase mb-1">
              Complexidade
            </p>
            <p className="font-medium capitalize">
              {classification?.complexity || "N/A"}
            </p>
          </div>

          {classification?.characteristics && classification.characteristics.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                Características
              </h3>
              <div className="flex flex-wrap gap-2">
                {classification.characteristics.map((c: string, i: number) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}

          {classification?.needsOCR && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
              ⚠️ Este documento pode requerer OCR para extração completa de texto.
            </div>
          )}
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          📋 Pré-visualização de blocos (primeira página)
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="pb-2 font-medium text-gray-500">#</th>
                <th className="pb-2 font-medium text-gray-500">Tipo</th>
                <th className="pb-2 font-medium text-gray-500">Texto</th>
                <th className="pb-2 font-medium text-gray-500">Fonte</th>
                <th className="pb-2 font-medium text-gray-500">Tamanho</th>
              </tr>
            </thead>
            <tbody>
              {document.pages[0]?.textBlocks.slice(0, 10).map(
                (block: any, i: number) => (
                  <tr key={block.id} className="border-b border-gray-100">
                    <td className="py-2 text-gray-500">{i + 1}</td>
                    <td className="py-2 capitalize">{block.type}</td>
                    <td className="py-2 truncate max-w-[300px]">
                      {block.text}
                    </td>
                    <td className="py-2 text-gray-500 text-xs">
                      {block.font?.family || "N/A"}
                    </td>
                    <td className="py-2 text-gray-500 text-xs">
                      {block.font?.size || "N/A"}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
