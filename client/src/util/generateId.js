// utility to generate ids
let current = 0

export default function generateId (prefix) {
  return `${prefix || 'id'}-${current++}`
}

export function resetIdCounter () { current = 0 }
