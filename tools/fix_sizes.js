const fs = require("fs");
const path = "/app/src/pages/Product.tsx";
let content = fs.readFileSync(path, "utf8");

const oldCode = `const displayedVariations = useMemo(() => {
    const vars = Array.isArray(product?.variations) ? product.variations : [];
    const selectedColor = selectedColorFromUrl;
    if (!selectedColor) return vars;
    return vars.filter((v: any) => {
      const { color } = parseVariation(String(v?.name || ""));
      return color && color.toLowerCase() === selectedColor.toLowerCase();
    });
  }, [product, selectedColorFromUrl]);`;

const newCode = `const sizeOrder: Record<string, number> = {
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
  }, [product, selectedColorFromUrl]);`;

content = content.replace(oldCode, newCode);
fs.writeFileSync(path, content);
console.log("Fixed!");