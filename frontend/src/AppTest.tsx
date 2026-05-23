export default function AppTest() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', textAlign: 'center' }}>
      <h1>Weather Pipeline Dashboard</h1>
      <p style={{ fontSize: '18px', color: '#666' }}>Frontend is working!</p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
        <p><strong>Backend Status:</strong> Check http://localhost:8000/api/health</p>
        <p><strong>Frontend Port:</strong> 3000</p>
      </div>
    </div>
  )
}
