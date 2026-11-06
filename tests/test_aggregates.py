import pytest
from test_core import collect

@pytest.mark.parametrize('language,source',[
 ('c','struct Pair {int left; int right;};\nint main(){\n struct Pair pair={7,21};\n int items[3]={4,8,21};\n return pair.right-items[2];\n}\n'),
 ('cpp','struct Pair {int left; int right;};\nint main(){\n Pair pair{7,21};\n int items[3]={4,8,21};\n return pair.right-items[2];\n}\n'),
 ('rust','#[derive(Debug)]\nstruct Pair {left:i32,right:i32}\nfn main(){\n let pair=Pair{left:7,right:21};\n let items=[4,8,21];\n println!("{} {}",pair.right,items[2]);\n}\n'),
])
def test_real_native_aggregate_fields(language,source):
    trace=collect({'language':language,'source':source,'maxEvents':200})
    assert trace['status']=='completed',trace['diagnostics']
    values=[value for event in trace['events'] for value in event['values'].values()]
    def fields(value):
        yield from value.get('children',{}).items()
        for child in value.get('children',{}).values():yield from fields(child)
    # C++ MI keeps fields under public/private/protected access groups.
    assert any(name=='right' and child['value']=='21' for value in values for name,child in fields(value)),values
    assert any(any(child.get('value')=='21' for child in value.get('children',{}).values()) for value in values if '[' in value['type']),values
