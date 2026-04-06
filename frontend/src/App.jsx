
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
            setResults(resultResponse.data.result);
            if (resultResponse.data.result.graph) {
              setGraph({
                nodes: resultResponse.data.result.graph.nodes,
                links: resultResponse.data.result.graph.edges.map(e => ({...e, source: e.source, target: e.target}))
              });
            }
            setLoading(false);
          } else if (resultResponse.data.status === 'PENDING' && attempts < maxAttempts) {
            setTimeout(checkResult, 3000);
          } else {
            console.error('Task failed or timeout');
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

  return (
    <div style={{fontFamily:'Arial',padding:20}}>
      <h1>Buscador OSINT – PCDF</h1>
      
      <div style={{marginBottom:20}}>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Digite CPF, Nome, E-mail, Telefone ou Vulgo"
          style={{padding:10, width:300, marginRight:10}}
        />
        <button onClick={handleSearch} disabled={loading || !token}>
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
        {!token && <span style={{marginLeft:10, color:'red'}}>Carregando token...</span>}
      </div>

      {results && (
        <div style={{display:'flex', gap:20}}>
          <div style={{flex:1}}>
            <h3>Resultados</h3>
            <pre style={{background:'#f5f5f5', padding:10, maxHeight:400, overflow:'auto'}}>
              {JSON.stringify(results.results, null, 2)}
            </pre>
          </div>
          
          <div style={{flex:1}}>
            <h3>Grafo de Vínculos</h3>
            <div style={{height:400, border:'1px solid #ccc'}}>
              <ForceGraph2D graphData={graph} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
