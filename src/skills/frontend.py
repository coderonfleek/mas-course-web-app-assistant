FRONTEND_SKILL = {
    "name": "frontend",
    "description": "Browser rendering, JavaScript errors, React/Vue issues, CSS problems, build/bundling, and DevTools debugging",
    "content": """# Frontend Troubleshooting Guide

## Quick Diagnostic Checklist

1. Open Browser DevTools (F12 or Cmd+Option+I)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed requests
4. Check Elements tab for DOM issues
5. Try incognito mode to rule out extensions/cache

---

## Common Issues and Solutions

### 1. Blank White Screen

**Symptoms:** Page loads but shows nothing

**Common Causes:**

a) **JavaScript Error Preventing Render**
   - Check Console for errors
   - Look for "Uncaught TypeError" or "Uncaught ReferenceError"
   - Fix: Trace the error and fix the null/undefined access

b) **Environment Variables Not Loaded**
   - React: Must prefix with REACT_APP_
   - Vite: Must prefix with VITE_
   - Next.js: Use NEXT_PUBLIC_ for client-side
   - Fix: Check .env file and rebuild

c) **Build Configuration Issue**
   - Missing polyfills for older browsers
   - Incorrect publicPath/base URL
   - Fix: Check bundler config (webpack.config.js, vite.config.js)

d) **"process is not defined" Error**
   - Node.js code running in browser
   - Fix for Vite: Use import.meta.env instead of process.env
   - Fix for Webpack 5: Add ProvidePlugin for process/buffer

### 2. React Hydration Errors

**Symptoms:** "Hydration failed because the initial UI does not match"

**Common Causes:**

a) **Server/Client HTML Mismatch**
   - Date/time rendering differently
   - Browser extensions injecting content
   - Fix: Use suppressHydrationWarning for dynamic content
   
b) **Invalid HTML Nesting**
   - <p> inside <p>
   - <div> inside <p>
   - Fix: Validate HTML structure

c) **useEffect Setting State on Mount**
   - State changes between server and client render
   - Fix: Use useLayoutEffect or check typeof window

### 3. CSS Not Applying

**Symptoms:** Styles missing or wrong

**Debugging Steps:**

a) **Check Specificity**
   - Open Elements tab, check Computed styles
   - Look for crossed-out rules
   - Fix: Increase specificity or use !important (last resort)

b) **Check for Typos**
   - Class name mismatch (case-sensitive!)
   - CSS Modules: Use styles.className not "className"
   
c) **Z-Index Issues**
   - Elements hidden behind others
   - Fix: Check stacking contexts, ensure parent has position

d) **Flexbox/Grid Not Working**
   - Parent needs display: flex/grid
   - Check flex-direction, justify-content, align-items

### 4. JavaScript Errors

**"Cannot read property 'x' of undefined"**
```javascript
// Problem
const value = obj.nested.property; // obj.nested is undefined

// Solution 1: Optional chaining
const value = obj?.nested?.property;

// Solution 2: Default values
const value = (obj.nested || {}).property;
```

**"x is not a function"**
```javascript
// Problem: Wrong import
import MyComponent from './MyComponent'; // default export
import { MyComponent } from './MyComponent'; // named export

// Check the export type in the source file
```

**"Cannot access before initialization"**
```javascript
// Problem: Temporal dead zone
console.log(x); // Error!
const x = 5;

// Solution: Move declaration before usage
const x = 5;
console.log(x);
```

### 5. React State Not Updating

**Symptoms:** UI doesn't reflect state changes

**Common Causes:**

a) **Mutating State Directly**
```javascript
// WRONG
state.items.push(newItem);
setState(state);

// CORRECT
setState({ ...state, items: [...state.items, newItem] });
```

b) **Stale Closure in useEffect**
```javascript
// WRONG
useEffect(() => {
  setInterval(() => console.log(count), 1000);
}, []); // count is stale

// CORRECT
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000);
  return () => clearInterval(id);
}, [count]);
```

c) **Async State Updates**
```javascript
// useState is async, use callback form
setCount(prev => prev + 1);
```

### 6. Build/Bundle Issues

**Large Bundle Size**
```bash
# Analyze bundle
npx webpack-bundle-analyzer stats.json
npx vite-bundle-visualizer

# Solutions:
# - Code splitting with dynamic imports
# - Tree shaking (ensure ES modules)
# - Remove unused dependencies
```

**Module Not Found**
```bash
# Check node_modules exists
npm install

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check import path (case-sensitive on Linux!)
```

---

## Browser DevTools Tips

### Console Tab
- `console.table(array)` - Pretty print arrays/objects
- `console.trace()` - Show call stack
- `$0` - Reference to selected element in Elements tab
- `copy(object)` - Copy to clipboard

### Network Tab
- Filter by XHR to see API calls
- Right-click > Copy as cURL
- Check Timing for slow requests
- Look for red failed requests

### Elements Tab
- Force element state (:hover, :active)
- Edit HTML/CSS live
- Check computed styles
- Monitor DOM breakpoints

### Performance Tab
- Record and analyze rendering
- Look for long tasks (> 50ms)
- Check for layout thrashing

---

## Framework-Specific Issues

### React
- Use React DevTools extension
- Check for missing keys in lists
- Profile re-renders with Profiler

### Vue
- Use Vue DevTools extension
- Check reactive data in component inspector
- Verify computed properties are caching

### Next.js
- Check for client/server component mismatch
- Verify API routes are correct
- Check next.config.js for issues
"""
}
