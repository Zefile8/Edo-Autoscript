import re
# list of autoscriptable psct to look for
cases = '''
once per turn:|
" once per turn|
 target |
 destroy |
 then |
and if you do|
 also |
\(quick effect\):|
    '''
base_target = 'function s.target(e,tp,eg,ep,ev,re,r,rp,chk,chkc)\n	<edit target>\nend'
base_activate = 'function s.activate(e,tp,eg,ep,ev,re,r,rp)\n	<edit activate>\nend'
cases = str(cases.replace('\n', ''))
def scriptranslate(psct):
    res = re.search(cases, psct)
    # check if something is scriptable
    if res is None:
        return ('All autoscripts done.','','')
    # find what option to autoscript
    match res[0]:
        case '" once per turn':
            return (res[0],'<expand effect>','e1:SetCountLimit(1,{id,0})\n	<expand effect>')
            
        case 'once per turn:':
            return (res[0],'<expand effect>','e1:SetCountLimit(1)\n	<expand effect>','<edit settype>','EFFECT_TYPE_IGNITION','<edit setcode>','EVENT_FREE_CHAIN')
            
        case ' target ':
            return (res[0],'<add func>','function s.filter(c)\n	return <filter>\nend','<add target>',base_target,'<edit target>','if chkc then return chkc:IsOnField() and s.filter(chkc) end\n	if chk==0 then return Duel.IsExistingTarget(s.filter,tp,LOCATION_ONFIELD,LOCATION_ONFIELD,1,nil) end\n	Duel.Hint(HINT_SELECTMSG,tp,<hint>)\n	local g=Duel.SelectTarget(tp,s.filter,tp,LOCATION_ONFIELD,LOCATION_ONFIELD,1,1,nil)\n	<edit target>','<add activate>',base_activate,'<edit activate>','local tc=Duel.GetFirstTarget()\n	if tc:IsRelateToEffect(e) then\n		<edit activate>\n	end','<expand effect>','e1:SetProperty(EFFECT_FLAG_CARD_TARGET)\n	<expand effect>')

        case ' destroy ':
            return (res[0],'<add target>',base_target,'<edit target>','<edit target>\n	Duel.SetOperationInfo(0,CATEGORY_DESTROY,g,1,0,0)','<add activate>',base_activate,'<edit activate>','Duel.Destroy(tc,REASON_EFFECT)\n	<edit activate>','<hint>','HINTMSG_DESTROY')
            
        case ' then ':
            return (res[0],'<edit activate>','Duel.BreakEffect()\n	<edit activate>')
            
        case 'and if you do':
            return(res[0],'<edit activate>','if <condition first part effect>\n		<edit activate>\n	end')
            
        case ' also ':
            return(res[0])
            
        case '(quick effect):':
            return(res[0],'<edit settype>','EFFECT_TYPE_QUICK_O','<edit setcode>','EVENT_FREE_CHAIN')
            
# "return" structured as follow:
# (case found, toreplace, replacement, toreplace, replacement,...)
# "case found" must be rewritten if regex characters are used
# as many replacements as you want (executed from left to right)
# put back the replacement tag at the end of each replacement
# "base_..." are templates that are used in many but not all cards