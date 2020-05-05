_manifest:
    #define TOKEN_TYPE_ID 3
    #define TOKEN_TYPE_FLOAT 4
    #define TOKEN_TYPE_WS 5
    #define TOKEN_TYPE_NUM 6
    #define TOKEN_TYPE_IF 7
    #define TOKEN_TYPE_THEN 8
    #define TOKEN_TYPE_ELSE 9
    #define TOKEN_TYPE_EQ 10
    #define TOKEN_TYPE_ASSIGN 11
_defines:
    whitespace     %{ |\n}%
    digit          %{[1-9]}%
    letter         %{[a-z]|[A-Z]}%
    number         %{{digit}{digit}*}%
    word           %{{letter}{letter}*}%
_patterns:
    ws             %{{whitespace}*}%                #{ token->set_token_type(TOKEN_TYPE_WS); token->set_ignore(true); }#
    num            %{{number}}%                     #{ token->set_token_type(TOKEN_TYPE_NUM); }#
    float          %{(0|{number}).[0-9]*}%          #{ token->set_token_type(TOKEN_TYPE_FLOAT); }#
    if             %{if}%                           #{ token->set_token_type(TOKEN_TYPE_IF); }#
    then           %{then}%                         #{ token->set_token_type(TOKEN_TYPE_THEN); }#
    else           %{else}%                         #{ token->set_token_type(TOKEN_TYPE_ELSE); }#
    eq             %{==}%                           #{ token->set_token_type(TOKEN_TYPE_EQ); }#
    assign         %{=}%                            #{ token->set_token_type(TOKEN_TYPE_ASSIGN); }#
    identifier     %{{word}}%                       #{ token->set_token_type(TOKEN_TYPE_ID); }#