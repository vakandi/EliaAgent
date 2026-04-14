#!/bin/sh

cat > /tmp/replacement.txt << 'ENDFILE'
  const sizeOrder: Record<string, number> = {
    "XXS": 1, "XS": 2, "S": 3, "M": 4, "L": 5, "XL": 6, "XXL": 7, "3XL": 8, "4XL": 9,
    "36": 20, "37": 21, "38": 22, "39": 23, "40": 24, "41": 25, "42": 26, "43": 27, "44": 28, "45": 29,
    "S/M": 50, "M/L": 51, "L/XL": 52
  };

  const getSizeOrder = (name: string): number => {
    const upper = (name || "").toUpperCase().trim();
    return sizeOrder[upper] !== undefined 
      ? sizeOrder[upper] 
      : 100 + name.localeCompare(name, undefined, { numeric: true });
  };

  const displayedVariations = useMemo(() => {
    const vars = Array.isArray(product?.variations) ? product.variations : [];
    const selectedColor = selectedColorFromUrl;
    
    let result = selectedColor
      ? vars.filter((v: any) => {
          const { color } = parseVariation(String(v?.name || ""));
          return color && color.toLowerCase() === selectedColor.toLowerCase();
        })
      : vars;

    return result.sort((a: any, b: any) => {
      const sizeA = parseVariation(a.name || "").size || a.name || "";
      const sizeB = parseVariation(b.name || "").size || b.name || "";
      return getSizeOrder(sizeA) - getSizeOrder(sizeB);
    });
  }, [product, selectedColorFromUrl]);
ENDFILE

LINE=$(grep -n "const displayedVariations = useMemo" /app/src/pages/Product.tsx | head -1 | cut -d: -f1)

if [ -n "$LINE" ]; then
  head -n $((LINE-1)) /app/src/pages/Product.tsx > /tmp/Product.tsx
  cat /tmp/replacement.txt >> /tmp/Product.tsx
  
  END_LINE=$(awk -v start=$LINE '/^  }, \[product, selectedColorFromUrl\]/ {print NR; exit}' /app/src/pages/Product.tsx)
  
  if [ -n "$END_LINE" ]; then
    tail -n +$((END_LINE+1)) /app/src/pages/Product.tsx >> /tmp/Product.tsx
    cp /tmp/Product.tsx /app/src/pages/Product.tsx
    echo "Fixed!"
  else
    echo "End not found"
  fi
else
  echo "Pattern not found"
fi