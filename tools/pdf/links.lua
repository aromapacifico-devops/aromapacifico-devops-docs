-- Runs on each document before they are joined. Links to another document of the
-- same PDF become links inside the PDF, links to other files of the repository
-- point to their page on GitHub, and every heading id carries the document prefix
-- so that headings with the same name in two documents stay apart.
local repo = "https://github.com/aromapacifico-devops/aromapacifico-devops-docs/blob/main/"
local doc_dir = os.getenv("DOC_DIR") or ""
local included = {}
for path in string.gmatch(os.getenv("PDF_INCLUDED") or "", "[^:]+") do
  included[path] = true
end

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

local function prefix(path)
  return "doc-" .. path:gsub("%.md$", ""):gsub("[^%w]", "-")
end

local own = prefix(os.getenv("DOC_PATH") or "")

function Header(el)
  el.identifier = own .. "-" .. el.identifier
  return el
end

function Link(el)
  local t = el.target
  if t:match("^%a+:") or t == "" then
    return el
  end
  if t:match("^#") then
    el.target = "#" .. own .. "-" .. t:sub(2)
    return el
  end
  local path, anchor = t:match("^([^#]*)#?(.*)$")
  local full = resolve(path)
  if included[full] then
    el.target = "#" .. prefix(full) .. (anchor ~= "" and ("-" .. anchor) or "")
  else
    el.target = repo .. full .. (anchor ~= "" and ("#" .. anchor) or "")
  end
  return el
end
