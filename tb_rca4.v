module tb_rca4(
    // reg input ports
    reg [3:0] a,
    reg cin,
    
    // wire output ports
    wire [3:0] sum,
    wire cout
);

rca4 dut (
    .a(a),
    .cin(cin),
    .sum(sum),
    .cout(cout)
);

initial begin
    // initialize signal values
    $display("Running test cases...");
    
    // all-zeros input pattern
    a = 0;
    cin = 0;
    #5;
    $display("Test case 1: All zeros");
    $display("  - Input a: %d, cin: %d", a, cin);
    $display("  - Output sum: %d, cout: %d", sum, cout);

    // all-ones input pattern
    a = $max(0, ~a+1);
    cin = 0;
    #5;
    $display("Test case 2: All ones");
    $display("  - Input a: %d, cin: %d", a, cin);
    $display("  - Output sum: %d, cout: %d", sum, cout);

    // boundary value input pattern
    a = $min(3, ~a+1);
    cin = 0;
    #5;
    $display("Test case 3: Boundary (min a)");
    $display("  - Input a: %d, cin: %d", a, cin);
    $display("  - Output sum: %d, cout: %d", sum, cout);

    // boundary value input pattern
    a = $max(0, ~a+1);
    cin = 0;
    #5;
    $display("Test case 4: Boundary (max a)");
    $display("  - Input a: %d, cin: %d", a, cin);
    $display("  - Output sum: %d, cout: %d", sum, cout);

    // alternating bit pattern
    for (int i = 0; i < 5; i++) begin
        #1;
        if (i%2 == 0) { a = ~a+1; } else { a = ~a; }
        cin = 0;
        
        $display("Test case %d: Alternating bit pattern", i+1);
        $display("  - Input a: %d, cin: %d", a, cin);
        $display("  - Output sum: %d, cout: %d", sum, cout);
    end
    
    // alternating bit pattern
    for (int i = 0; i < 5; i++) begin
        #1;
        if (i%2 == 0) { a = ~a+1; } else { a = ~a; }
        cin = 1;

        $display("Test case %d: Alternating bit pattern (cin=1)", i+1);
        $display("  - Input a: %d, cin: %d", a, cin);
        $display("  - Output sum: %d, cout: %d", sum, cout);
    end

endinitial begin
    
    // monitor signal changes
    $monitor("#%0d, tns = $time");
end

// endmodule keyword here (after the last module definition)
endmodule