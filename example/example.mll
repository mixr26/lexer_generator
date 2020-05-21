_manifest:
_tokens:
    ID
    FLOAT
    WS
    NUM
    IF
    THEN
    ELSE
    EQ
    ASSIGN
_defines:
    whitespace     %{ |\n}%
    digit          %{[1-9]}%
    letter         %{[a-z]|[A-Z]}%
    number         %{{digit}{digit}*}%
    word           %{{letter}{letter}*}%
_patterns:
    ws             %{{whitespace}*}%                #{ token->set_token_type(WS); token->set_ignore(true); }#
    num            %{{number}}%                     #{ token->set_token_type(NUM); }#
    float          %{(0|{number}).[0-9]*}%          #{ token->set_token_type(FLOAT); }#
    if             %{if}%                           #{ token->set_token_type(IF); }#
    then           %{then}%                         #{ token->set_token_type(THEN); }#
    else           %{else}%                         #{ token->set_token_type(ELSE); }#
    eq             %{==}%                           #{ token->set_token_type(EQ); }#
    assign         %{=}%                            #{ token->set_token_type(ASSIGN); }#
    identifier     %{{word}}%                       #{ token->set_token_type(ID); }#
