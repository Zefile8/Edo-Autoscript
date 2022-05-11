--<Card Name>
--Edo Autoscript written by Zefile#5500
local s,id = GetID()
function s.initial_effect(c)
	local e1=Effect.CreateEffect(c)
	e1:SetType(<edit settype>)
	e1:SetCode(<edit setcode>)
	<expand effect>
	c:RegisterEffect(e1)
    <expand initial>
end
<add condition>
<add target>
<add operation>
<add func>
--this is the default file Autoscript will produce if given no instructions.