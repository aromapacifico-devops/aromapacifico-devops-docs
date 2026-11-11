-- The first level 1 heading becomes the cover title, and links to files of the
-- repository point to their page on GitHub, since the PDF travels alone.
local repo = "https://github.com/aromapacifico-devops/aromapacifico-devops-docs/blob/main/"
local doc_dir = os.getenv("DOC_DIR") or ""

local function resolve(target)
  local parts = {}
  for part in string.gmatch(doc_dir .. "/" .. target, "[^/]+") do
    if part == ".." then
      table.remove(parts)
    elseif part ~= "." then
      table.insert(parts, part)
    end
  end
  return table.concat(parts, "/")
end

function Link(el)
  local t = el.target
  if t:match("^%a+:") or t:match("^#") or t == "" then
    return el
  end
  local path, anchor = t:match("^([^#]*)(#?.*)$")
  el.target = repo .. resolve(path) .. anchor
  return el
end

function Pandoc(doc)
  local blocks, found = {}, false
  for _, b in ipairs(doc.blocks) do
    if not found and b.t == "Header" and b.level == 1 then
      found = true
      doc.meta.title = b.content
    else
      table.insert(blocks, b)
    end
  end
  doc.blocks = blocks
  return doc
end
