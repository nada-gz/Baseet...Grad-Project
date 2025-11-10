This short tutorial summarizes key React concepts learned from the official [React Tic-Tac-Toe Tutorial](https://react.dev/learn/tutorial-tic-tac-toe).  
It helps new contributors quickly understand React fundamentals used in the Frontend part of our **Grad Project**.

---

## ⚙️ 1. Components
### Definition  
Components are reusable building blocks in React that define parts of the UI (like buttons, headers, or entire sections).

### Why React Uses It  
They let you split your UI into independent, manageable pieces — improving **reusability**, **organization**, and **maintainability**.

### How It’s Written  
\`\`\`jsx
// Example component
function Welcome() {
  return <h1>Hello, World!</h1>;
}
\`\`\`

### When to Use  
Whenever you need a reusable or logical piece of UI — like cards, forms, buttons, or sections.

---

## 💠 2. JSX
### Definition  
JSX (JavaScript XML) is a syntax extension that lets you write HTML-like code inside JavaScript.

### Why React Uses It  
It makes code easier to read and lets you combine UI markup and logic in one place.  
React converts JSX to regular JavaScript using `React.createElement()`.

### How It’s Written  
\`\`\`jsx
// JSX example
const element = <h1 className="title">Hello React!</h1>;
\`\`\`

### When to Use  
Use JSX anytime you define what your component should display.

---

## 📦 3. Props
### Definition  
Props (short for “properties”) are inputs passed to components to make them dynamic and reusable.

### Why React Uses It  
Props let parent components send data or configuration down to children, keeping components **flexible and independent**.

### How It’s Written  
\`\`\`jsx
// Props example
function Greeting(props) {
  return <h2>Hello, {props.name}!</h2>;
}
<Greeting name="Nada" />
\`\`\`

### When to Use  
When a child component needs data from its parent — for example, a username, title, or list of items.

---

## 🔁 4. State
### Definition  
State is data that changes over time within a component.

### Why React Uses It  
React re-renders the component whenever its state changes — keeping the UI always up to date with current data.

### How It’s Written  
\`\`\`jsx
// State example
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>You clicked {count} times.</p>
      <button onClick={() => setCount(count + 1)}>Click</button>
    </div>
  );
}
\`\`\`

### When to Use  
When you want to track data that changes (like user input, toggle status, or score in a game).

---

## 🧩 7. Conditional Rendering
### Definition  
React lets you show or hide elements based on conditions.

### How It’s Written  
\`\`\`jsx
// Conditional rendering example
{winner ? <p>Winner: {winner}</p> : <p>Next player: X</p>}
\`\`\`

EOF
