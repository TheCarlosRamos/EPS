
import React, { useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';

// Usa variável de ambiente ou localhost como padrão
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function App(){
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [graph, setGraph] = useState({nodes:[{id:'Investigado'}],links:[]});
  const [token, setToken] = useState(null);

  // Obter token ao carregar o componente
  useEffect(() => {
    const getToken = async () => {
      try {
        const response = await axios.post(`${API_URL}/login`);
        setToken(response.data.access_token);
      } catch (error) {
        console.error('Erro ao obter token:', error);
      }
    };
    getToken();
  }, []);

  const handleSearch = async () => {
    if (!query || !token) return;
    
    setLoading(true);
    setResults(null);
    try {
      const response = await axios.post(`${API_URL}/search`, 
        { query }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const taskId = response.data.task_id;
      console.log('Task ID:', taskId);
      
      // Poll for results com limite de tentativas
      let attempts = 0;
      const maxAttempts = 10;
      
      const checkResult = async () => {
        try {
          attempts++;
          console.log(`Checking task status, attempt ${attempts}`);
          
          const resultResponse = await axios.get(`${API_URL}/task/${taskId}`);
          console.log('Task response:', resultResponse.data);
          
          if (resultResponse.data.status === 'SUCCESS') {
            console.log('SUCCESS - Full response:', resultResponse.data);
            console.log('SUCCESS - Results:', resultResponse.data.result);
            setResults(resultResponse.data.result);
            if (resultResponse.data.result.graph) {
              console.log('SUCCESS - Graph data:', resultResponse.data.result.graph);
              setGraph({
                nodes: resultResponse.data.result.graph.nodes,
                links: resultResponse.data.result.graph.edges.map(e => ({...e, source: e.source, target: e.target}))
              });
            }
            setLoading(false);
          } else if (resultResponse.data.status === 'PENDING' && attempts < maxAttempts) {
            console.log('PENDING - checking again in 3 seconds');
            setTimeout(checkResult, 3000);
          } else {
            console.error('Task failed or timeout - status:', resultResponse.data.status);
            setLoading(false);
          }
        } catch (error) {
          console.error('Error checking task status:', error);
          if (attempts < maxAttempts) {
            setTimeout(checkResult, 3000);
          } else {
            setLoading(false);
          }
        }
      };
      
      checkResult();
    } catch (error) {
      console.error('Search error:', error);
      setLoading(false);
    }
  };

  const renderResults = () => {
    console.log('renderResults called with:', results);
    
    if (!results || !results.results || results.results.length === 0) {
      console.log('No results found');
      return (
        <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>
          <h3>Nenhum resultado encontrado</h3>
          <p>Tente usar termos diferentes ou verificar a conexão.</p>
        </div>
      );
    }

    console.log('Results found:', results.results.length);

    // Agrupar resultados por fonte
    const resultsBySource = {};
    results.results.forEach(item => {
      const source = item.source || 'desconhecido';
      if (!resultsBySource[source]) {
        resultsBySource[source] = [];
      }
      resultsBySource[source].push(item);
    });

    console.log('Results by source:', resultsBySource);

    return (
      <div>
        <h3>Resultados Encontrados ({results.results.length})</h3>
        {Object.entries(resultsBySource).map(([source, items]) => (
          <div key={source} style={{marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '5px'}}>
            <h4 style={{color: '#0066cc', margin: '0 0 10px 0'}}>
              📡 {source.charAt(0).toUpperCase() + source.slice(1)} ({items.length})
            </h4>
            {items.map((item, index) => (
              <div key={index} style={{marginBottom: '10px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '3px'}}>
                {item.title && <div><strong>Título:</strong> {item.title}</div>}
                {item.profile && <div><strong>Perfil:</strong> {item.profile}</div>}
                {item.url && (
                  <div>
                    <strong>URL:</strong> 
                    <a href={item.url} target="_blank" rel="noopener noreferrer" style={{color: '#0066cc', marginLeft: '5px'}}>
                      {item.url}
                    </a>
                  </div>
                )}
                {item.evidence && (
                  <div style={{fontSize: '12px', color: '#666'}}>
                    <strong>Evidência:</strong> {item.evidence}
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div style={{fontFamily:'Arial',padding:20}}>
      <h1>🔍 Buscador OSINT – PCDF</h1>
      
      <div style={{marginBottom:20}}>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Digite CPF, Nome, E-mail, Telefone ou Vulgo"
          style={{padding:10, width:300, marginRight:10}}
        />
        <button onClick={handleSearch} disabled={loading || !token}>
          {loading ? '🔍 Buscando...' : '🔎 Buscar'}
        </button>
        {!token && <span style={{marginLeft:10, color:'red'}}>🔐 Carregando token...</span>}
      </div>

      {results && (
        <div style={{display:'flex', gap:20}}>
          <div style={{flex:2}}>
            {renderResults()}
          </div>
          
          <div style={{flex:1}}>
            <h3>🕸️ Grafo de Vínculos</h3>
            <div style={{height:400, border:'1px solid #ccc', borderRadius: '5px'}}>
              <ForceGraph2D graphData={graph} />
            </div>
            <div style={{marginTop: '10px', fontSize: '12px', color: '#666'}}>
              {graph.nodes.length} nós • {graph.links.length} conexões
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
