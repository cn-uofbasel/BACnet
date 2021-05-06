-- BACnet dissector

cbor = Dissector.get("cbor")

bacnet_proto = Proto("BACevent",  "BACnet Event")
-- local b_meta = ProtoField.new("Meta", "extract.hex", ftypes.STRING)
-- local b_sign = ProtoField.new("Sign", "extract.hex", ftypes.STRING)
-- local b_cont = ProtoField.new("Cont", "extract.hex", ftypes.STRING)
-- bacnet_proto.fields = {b_meta, b_sign, b_cont}

bac_meta_proto = Proto("BACmeta",  "meta")
bac_cont_proto = Proto("BACcont",  "content")

function cbor_len(buf)
    -- returns number of bytes following this CBOR type
    b = buf(0,1):uint()
    if b >= 128 then b = b - 128 end
    if b >= 64 then b = b - 64 end
    if b >= 32 then b = b - 32 end
    if b < 24 then return b end
    if b == 24 then return buf(1,1):uint() end
    if b == 25 then return buf(1,2):uint() end
    return nil
end

function cbor_len_len(l)
    -- returns number of bytes needed for CBOR type and length
    r = 1
    if l > 23 then r = r + 1 end
    if l > 255 then r = r + 1 end
    return r
end


function bacnet_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "BACnet"
    tree = tree:add(bacnet_proto, buffer(), "BACnet Event")
    -- meta:
    local l1 = cbor_len(buffer(1,3))
    local ll1 = cbor_len_len(l1)
    local a1 = buffer(1+ll1,l1):tvb()
    subtree = tree:add(bac_meta_proto, buffer(1,ll1+l1))
    cbor:call(a1, pinfo, subtree)
    -- signature:
    local o2 = 1+ll1+l1
    local l2 = cbor_len(buffer(o2,3))
    local ll2 = cbor_len_len(l2)
    tree:add(buffer(o2+ll2, l2), "signature: " .. buffer(o2+ll2, l2))
    -- content:
    local o3 = 1 + ll1 + l1 + ll2 + l2
    local l3 = cbor_len(buffer(o3,3))
    local ll3 = cbor_len_len(l3)
    local a3 = buffer(o3+ll3,l3):tvb()
    subtree = tree:add(bac_cont_proto, buffer(o3,ll3+l3))
    cbor:call(a3, pinfo, subtree)
end


-- register our protocol as a postdissector
register_postdissector(bacnet_proto)

-- eof
