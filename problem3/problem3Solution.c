#include <stdio.h>
#include <stdlib.h>
#include <time.h>

double U() {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

void gen_ints() {
    printf("---- (a) 100 integers [0,99] ----\n");
    for (int i = 0; i < 100; i++) {
        int x = (int)(U() * 100.0);
        printf("%d ", x);
    }
    printf("\n\n");
}

void gen_floats() {
    printf("---- (b) 100 floats [0.25,0.5) ----\n");
    for (int i = 0; i < 100; i++) {
        double x = 0.25 + (0.5 - 0.25) * U();
        printf("%.4f ", x);
    }
    printf("\n\n");
}

void gen_mixture() {
    printf("---- (c) mixture distribution ----\n");
    for (int i = 0; i < 100; i++) {
        double r = U();
        if (r < 0.5) {
            printf("1 ");
        } else if (r < 0.7) {
            printf("2 ");
        } else {
            double x = 3.0 + U();   // [3,4)
            printf("%.4f ", x);
        }
    }
    printf("\n\n");
}

int main() {
    srand(time(NULL));

    gen_ints();
    gen_floats();
    gen_mixture();

    return 0;
}