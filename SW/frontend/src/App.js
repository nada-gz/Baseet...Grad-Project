import logo from './logo.svg';
import './App.css';
import TestBackend from './components/TestBackend';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      {/* Original React logo header */}
      <header className="App-header mb-6">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>

      {/* Tailwind test component */}
      <div className="p-6 max-w-sm bg-white rounded-lg shadow-md text-center">
        <h1 className="text-2xl font-bold text-blue-600 mb-4">
          Tailwind is working!
        </h1>
        <p className="text-gray-700">
          This component uses Tailwind classes for layout, color, and typography.
        </p>
        <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
          Click Me
        </button>
      </div>

      {/* Test backend connection */}
      <TestBackend />
    </div>
  );
}

export default App;
