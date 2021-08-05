// based on. https://matthiashager.com/converting-snake-case-to-camel-case-object-keys-with-javascript
const isObject = function (o: any) {
  return o === Object(o) && !Array.isArray(o) && typeof o !== 'function'
}

function toCamel(s: string) {
  return s.replace(/([-_][a-z])/gi, ($1) => {
    return $1.toUpperCase().replace('-', '').replace('_', '')
  })
}

function keysToCamel(o: any): any {
  if (isObject(o)) {
    const n: { [key: string]: any } = {}
    Object.keys(o).forEach((k) => {
      n[toCamel(k)] = keysToCamel(o[k])
    })
    return n
  } else if (Array.isArray(o)) {
    return o.map((i) => {
      return keysToCamel(i)
    })
  }
  return o
}

export function adaptTo<AdaptedType>(o: any): AdaptedType {
  return keysToCamel(o)
}
