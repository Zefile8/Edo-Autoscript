import re
# list of autoscriptable psct to look for
cases_list = '''
once per turn:|
" once per turn|
target |
destroy |
then|
and if you do|
also|
\(quick effect\):|
from your deck to your hand|
except "|
    '''
cases_list = str(cases_list.replace('\n', ''))

# a few templates used in many cases
base_target = 'function s.target(e,tp,eg,ep,ev,re,r,rp,chk,chkc)\n	<edit target>\nend'
target_initial = 'e1:SetTarget(s.target)\n	<expand effect>'
base_operation = 'function s.operation(e,tp,eg,ep,ev,re,r,rp)\n	<edit operation>\nend'
operation_initial = 'e1:SetTarget(s.operation)\n	<expand effect>'
base_filter = 'function s.filter(c)\n	return <filter>\nend\n<add func>'

# func that finds the scriptable bit and returns the corresponding script
def scriptranslate(psct):
    res = re.search(cases_list, psct)
    # check if something is scriptable
    if res is None:
        return ('All autoscripts done.','','')
    # find what option to autoscript
    match res[0]:
        case '" once per turn':
            return (res[0],'<expand effect>','e1:SetCountLimit(1,{id,0})\n	<expand effect>')
            
        case 'once per turn:':
            return (res[0],'<expand effect>','e1:SetCountLimit(1)\n	<expand effect>','<edit settype>','EFFECT_TYPE_IGNITION','<edit setcode>','EVENT_FREE_CHAIN')
            
        case 'target ':
            return (res[0],'<add func>',base_filter,'<expand effect>',target_initial,'<add target>',base_target,'<edit target>','if chkc then return chkc:IsOnField() and s.filter(chkc) end\n	if chk==0 then return Duel.IsExistingTarget(s.filter,tp,LOCATION_ONFIELD,LOCATION_ONFIELD,1,nil) end\n	Duel.Hint(HINT_SELECTMSG,tp,<hint>)\n	local g=Duel.SelectTarget(tp,s.filter,tp,LOCATION_ONFIELD,LOCATION_ONFIELD,1,1,nil)\n	<edit target>','<expand effect>',operation_initial,'<add operation>',base_operation,'<edit operation>','local tc=Duel.GetFirstTarget()\n	if tc:IsRelateToEffect(e) then\n		<edit operation>\n	end','<expand effect>','e1:SetProperty(EFFECT_FLAG_CARD_TARGET)\n	<expand effect>')
            
        case 'destroy ':
            return (res[0],'<expand effect>',target_initial,'<add target>',base_target,'<edit target>','<edit target>\n	Duel.SetOperationInfo(0,CATEGORY_DESTROY,g,1,0,0)','<expand effect>',operation_initial,'<add operation>',base_operation,'<edit operation>','Duel.Destroy(tc,REASON_EFFECT)\n	<edit operation>','<hint>','HINTMSG_DESTROY')
            
        case 'then':
            return (res[0],'<expand effect>',operation_initial,'<add operation>',base_operation,'<edit operation>','if <condition first part effect>\n		Duel.BreakEffect()\n		<edit operation>\n	end')
            
        case 'and if you do':
            return(res[0],'<expand effect>',operation_initial,'<add operation>',base_operation,'<edit operation>','if <condition first part effect>\n		<edit operation>\n	end')
            
        case 'also':
            return(res[0],'<expand effect>',operation_initial,'<add operation>',base_operation)
            
        case '(quick effect):':
            return(res[0],'<edit settype>','EFFECT_TYPE_QUICK_O','<edit setcode>','EVENT_FREE_CHAIN')
            
        case 'from your deck to your hand':
            return(res[0],'<expand effect>','e1:SetCategory(CATEGORY_TOHAND+CATEGORY_SEARCH)\n	<expand effect>','<expand effect>',target_initial,'<add target>',base_target,'<expand effect>',operation_initial,'<add operation>',base_operation,'<edit target>','if chk==0 then return Duel.IsExistingMatchingCard(s.filter,tp,LOCATION_DECK,0,1,nil) end\n	<edit target>\n	Duel.SetOperationInfo(0,CATEGORY_TOHAND,nil,1,tp,LOCATION_DECK)','<edit operation>','Duel.Hint(HINT_SELECTMSG,tp,HINTMSG_ATOHAND)\n	local g=Duel.SelectMatchingCard(tp,s.filter,tp,LOCATION_DECK,0,1,1,nil)\n	if #g>0 then\n		Duel.SendtoHand(g,nil,REASON_EFFECT)\n		Duel.ConfirmCards(1-tp,g)\n	end\n	<edit operation>','<add func>',base_filter,'<filter>','c:IsAbleToHand() and <filter>')
        
        case 'except "':
            return(res[0],'<filter>','not c:IsCode(id) and <filter>','<add func>','s.listed_names={id}\n<add func>')
        
# "return" structured as follow:
# (case found, toreplace, replacement, toreplace, replacement,...)
# as many replacements as you want (executed from left to right)
# put back the replacement tag at the end of each replacement
# characters in cases_list that are used by regex must be escaped (see quick effect case)
# "base_..." are templates that are used in many but not all cards