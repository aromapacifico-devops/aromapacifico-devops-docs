-- The first level 1 heading of the joined document becomes the cover title.
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
