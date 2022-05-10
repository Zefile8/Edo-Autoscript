import re
# list of autoscriptable psct to look for
cases_list = '''
once per turn:|
" once per turn|
can only be activated once per turn|
can only be used once per turn|
target |
destroy |
then|
and if you do|
also|
\(quick effect\):|
from your deck to your hand|
except "|
special summon|
you cannot special summon for the rest of this turn, except|
draw|
1 |
2 |
3 |
4 |
5 |
6 |
7 |
8 |
9 |
    '''
# next, add a bunch of FROMs
cases_list = str(cases_list.replace('\n', ''))

# a few templates used in many cases
base_target = 'function s.target(e,tp,eg,ep,ev,re,r,rp,chk,chkc)\n	<edit target>\nend'
target_initial = 'e1:SetTarget(s.target)\n	<expand effect>'
add_target = ('<expand effect>',target_initial,'<add target>',base_target)
base_operation = 'function s.operation(e,tp,eg,ep,ev,re,r,rp)\n	<edit operation>\nend'
operation_initial = 'e1:SetTarget(s.operation)\n	<expand effect>'
add_operation = ('<expand effect>',operation_initial,'<add operation>',base_operation)
base_condition = 'function s.condition(e,tp,eg,ep,ev,re,r,rp)\n	<edit condition>\nend'
condition_initial = 'e1:SetCondition(s.condition)\n	<expand effect>'
add_condition = ('<expand effect>',condition_initial,'<add condition>',base_condition)
base_filter = 'function s.filter(c)\n	return <filter>\nend\n<add func>'

# func that finds the scriptable bit and returns the corresponding script
def scriptranslate(psct):
    res = re.search(cases_list, psct)
    # check if something is scriptable
    if res is None:
        return ('All autoscripts done.',0,'','')
    # find what option to autoscript
    match res[0]:
        case '" once per turn':
            return (res[0],1,'<expand effect>','e1:SetCountLimit(1,{id,0})\n	<expand effect>')
        
        case 'can only be activated once per turn':
            return (res[0],1,'<expand effect>','e1:SetCountLimit(1,{id,0})\n	<expand effect>')

        case 'can only be used once per turn':
            return (res[0],1,'<expand effect>','e1:SetCountLimit(1,{id,0})\n	<expand effect>')

        case 'once per chain':
            return (res[0],1)+add_condition+('<edit condition>','if e:GetHandler():IsStatus(STATUS_CHAINING) then return false end\n	<edit condition>')
        
        case 'once per turn:':
            return (res[0],1,'<expand effect>','e1:SetCountLimit(1)\n	<expand effect>','<edit settype>','EFFECT_TYPE_IGNITION','<edit setcode>','EVENT_FREE_CHAIN')
        
        case 'target ':
            return (res[0],1,'<add func>',base_filter)+add_target+add_operation+('<edit target>','if chkc then return chkc:IsOnField() and s.filter(chkc) end\n	if chk==0 then return Duel.IsExistingTarget(s.filter,tp,LOCATION_ONFIELD,LOCATION_ONFIELD,1,nil) end\n	Duel.Hint(HINT_SELECTMSG,tp,<hint>)\n	local g=Duel.SelectTarget(tp,s.filter,tp,LOCATION_ONFIELD,LOCATION_ONFIELD,1,1,nil)\n	<edit target>','<edit operation>','local tc=Duel.GetFirstTarget()\n	if tc:IsRelateToEffect(e) then\n		<edit operation>\n	end','<expand effect>','e1:SetProperty(EFFECT_FLAG_CARD_TARGET)\n	<expand effect>')
        
        case 'destroy ':
            return (res[0],1)+add_target+add_operation+('<edit target>','<edit target>\n	Duel.SetOperationInfo(0,CATEGORY_DESTROY,g,1,0,0)','<edit operation>','Duel.Destroy(tc,REASON_EFFECT)\n	<edit operation>','<hint>','HINTMSG_DESTROY')
        
        case 'then':
            return (res[0],1)+add_operation+('<edit operation>','if <condition first part effect>\n		Duel.BreakEffect()\n		<edit operation>\n	end')
        
        case 'and if you do':
            return (res[0],1)+add_operation+('<edit operation>','if <condition first part effect>\n		<edit operation>\n	end')
        
        case 'also':
            return (res[0],1,)+add_operation
        
        case '(quick effect):':
            return (res[0],1,'<edit settype>','EFFECT_TYPE_QUICK_O','<edit setcode>','EVENT_FREE_CHAIN')
        
        case 'from your deck to your hand':
            return (res[0],1,'<expand effect>','e1:SetCategory(CATEGORY_TOHAND+CATEGORY_SEARCH)\n	<expand effect>')+add_target+add_operation+('<edit target>','if chk==0 then return Duel.IsExistingMatchingCard(s.filter,tp,LOCATION_DECK,0,1,nil) end\n	<edit target>\n	Duel.SetOperationInfo(0,CATEGORY_TOHAND,nil,1,tp,LOCATION_DECK)','<edit operation>','Duel.Hint(HINT_SELECTMSG,tp,HINTMSG_ATOHAND)\n	local g=Duel.SelectMatchingCard(tp,s.filter,tp,LOCATION_DECK,0,1,1,nil)\n	if #g>0 then\n		Duel.SendtoHand(g,nil,REASON_EFFECT)\n		Duel.ConfirmCards(1-tp,g)\n	end\n	<edit operation>','<add func>',base_filter,'<filter>','c:IsAbleToHand() and <filter>')
        
        case 'except "':
            return (res[0],1,'<filter>','not c:IsCode(id) and <filter>','<add func>','s.listed_names={id}\n<add func>')
        
        case 'special summon':
            return (res[0],1,'<add func>',base_filter)+add_target+add_operation+('<expand effect>','e1:SetCategory(CATEGORY_SPECIAL_SUMMON)\n	<expand effect>','<edit target>','if chk==0 then return Duel.GetLocationCount(tp,LOCATION_MZONE)>0\n		and Duel.IsExistingMatchingCard(s.filter,tp,<from>,0,1,nil,e,tp) end\n	Duel.SetOperationInfo(0,CATEGORY_SPECIAL_SUMMON,nil,1,0,<from>)\n	<edit target>','<edit operation>','if Duel.GetLocationCount(tp,LOCATION_MZONE)<<amount> then return end\n	Duel.Hint(HINT_SELECTMSG,tp,HINTMSG_SPSUMMON)\n	local g=Duel.SelectMatchingCard(tp,s.filter,tp,<from>,0,1,<amount>,nil,e,tp)\n	if #g>Duel.GetLocationCount(tp,LOCATION_MZONE) then\n	Duel.SpecialSummon(g,0,tp,tp,false,false,POS_FACEUP)\n	<edit operation>')
        
        case 'you cannot special summon for the rest of this turn, except':
            return (res[0],1)+add_operation+('<edit operation>','local e1=Effect.CreateEffect(c)\n	e1:SetDescription(aux.Stringid(id,2))\n	e1:SetType(EFFECT_TYPE_FIELD)\n	e1:SetCode(EFFECT_CANNOT_SPECIAL_SUMMON)\n	e1:SetProperty(EFFECT_FLAG_PLAYER_TARGET+EFFECT_FLAG_CLIENT_HINT)\n	e1:SetTargetRange(1,0)\n	e1:SetTarget(s.splimit)\n	e1:SetReset(RESET_PHASE+PHASE_END)\n	Duel.RegisterEffect(e1,tp)\n	<edit operation>','<add func>','function s.splimit(e,c)\n	return not <filter>\nend\n<add func>')
        
        case 'draw':
            return (res[0],1,'<expand effect>','e1:SetCategory(CATEGORY_DRAW)\n	e1:SetProperty(EFFECT_FLAG_PLAYER_TARGET)\n	<expand effect>')+add_target+add_operation+('<edit target>','if chk==0 then return Duel.IsPlayerCanDraw(tp,<amount>) end\n	Duel.SetTargetPlayer(tp)\n	Duel.SetTargetParam(<amount>)\n	Duel.SetOperationInfo(0,CATEGORY_DRAW,nil,0,tp,2)\n	<edit target>','<edit operation>','local p,d=Duel.GetChainInfo(0,CHAININFO_TARGET_PLAYER,CHAININFO_TARGET_PARAM)\n	Duel.Draw(p,d,REASON_EFFECT)\n	<edit operation>')
        
        case '1 ':
            return (res[0],99,'<amount>','1')
        case '2 ':
            return (res[0],99,'<amount>','2')
        case '3 ':
            return (res[0],99,'<amount>','3')
        case '4 ':
            return (res[0],99,'<amount>','4')
        case '5 ':
            return (res[0],99,'<amount>','5')
        case '6 ':
            return (res[0],99,'<amount>','6')
        case '7 ':
            return (res[0],99,'<amount>','7')
        case '8 ':
            return (res[0],99,'<amount>','8')
        case '9 ':
            return (res[0],99,'<amount>','9')
        
    return("error", 101, "out of case switch", "")

# "return" structured as follow:
# (case found, amount of allowed replacements, toreplace, replacement, toreplace, replacement,...)
# as many replacements as you want (executed from left to right)
# put back the replacement tag at the end of each replacement
# characters in cases_list that are used by regex must be escaped (see quick effect case)
# "base_..." are templates that are used in many but not all cards