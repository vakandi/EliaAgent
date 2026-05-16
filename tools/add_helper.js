const fs=require("fs");
let c=fs.readFileSync("/app/src/pages/Product.tsx","utf8");
c=c.replace("const parseVariation","const sizeOrderMap={XXS:1,XS:2,S:3,M:4,L:5,XL:6,XXL:7}; const sortBySize=(a)=>{const g=n=>sizeOrderMap[n?.toUpperCase()]||99;return[...a].sort((x,y)=>{const sx=parseVariation(x?.name||'').size||x?.name||'';const sy=parseVariation(y?.name||'').size||y?.name||'';return g(sx)-g(sy)})}; const parseVariation");
fs.writeFileSync("/app/src/pages/Product.tsx",c);
console.log("done");